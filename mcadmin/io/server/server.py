import atexit
import collections
import datetime
import glob
import logging
import os
import signal
import threading
import time
from enum import Enum
from subprocess import Popen, PIPE

import requests

from mcadmin.config import CONFIG
from mcadmin.io.files.server_list import SERVER_LIST

_EULA_TXT = 'eula.txt'
_LOGGER = logging.getLogger(__name__)

# Maximum amount of times to try to download a server executable from the internet
_MAX_DOWNLOAD_ATTEMPTS = 2

# Maximum amount of time to wait for a process to end
_SIGTERM_WAIT_SECONDS = 30

# Maximum amount of lines that there can be inside the console_output deque
_CONSOLE_OUTPUT_MAX_LINES = 100


def _timedelta_to_seconds(dt):
    return dt.days * 86400 + dt.seconds


class TooManyMatchesError(Exception):
    """
    For when a lookup returns more than one match when just one is expected.
    """


class ServerAlreadyRunningError(Exception):
    """
    Raised when trying to start the server when it is already running.
    """


class ServerNotRunningError(Exception):
    """
    Raised when an action that requires a running server is performed without the server running.
    """


class ServerStatus(Enum):
    """
    Enum for representing server statuses. See Server.is_running() for usage.
    """
    RUNNING = 'running'
    CLOSED = 'closed'
    DISABLED = 'disabled'


class Server:

    def __init__(self, dir_):
        self.DIR = dir_

        self.console_output = collections.deque(maxlen=_CONSOLE_OUTPUT_MAX_LINES)

        # Notified every time the server status change from ON to OFF or vice-versa.
        self.STATUS_CHANGE = threading.Condition()

        # Notified whenever there is a console output
        self.OUTPUT_UPDATE = threading.Condition()

        # Java Process Handle
        self._proc = None  # type: Popen or None
        self._PROC_LOCK = threading.RLock()

        self._start_time = None  # type: datetime.datetime or None

    @property
    def jar(self):
        return CONFIG.get_use_jar()

    def autostart(self, *args, **kwargs):
        """
        Starts the server and automatically downloads the latest stable version no jar is configured. Updates the
        config with the new jar.

        If the jar is configured but not found in the filesystem, it will try to download it.
        """
        if not self.jar:
            # Jar is not _set
            CONFIG.set_use_jar(self._download_latest_vanilla_server())

        elif not os.path.exists(self.jarpath()):
            # Jar is _set but it doesn't exist
            # Try to download the jar
            versions = SERVER_LIST.versions()

            found = [(version, full_name, link)
                     for version, full_name, link in versions['stable'] + versions['snapshot']
                     if full_name == self.jar]
            if len(found) == 0:
                raise FileNotFoundError('%s not found for download' % self.jar)
            if len(found) > 1:
                raise ValueError('More than one link found for %s: %s' % (self.jar, str(found)))

            version, full_name, link = found[0]
            _LOGGER.info('Downloading %s...' % link)
            self._download(link, dest_name=full_name)

        assert self.jar
        self.start(*args, **kwargs)

    def start(self, jvm_params=''):
        """
        Starts the server. Will use the jar in `self.jar`.

        :param str jvm_params: Parameters used when starting the JVM. Nothing by default.

        :raise ServerAlreadyRunningError: If the server is already running.
        :raise FileNotFoundError: If `server_jar_name` param was specified but a file by that name was not found inside
                                  the server directory.
        """
        # Create server files directory if it does not exist.
        if not os.path.exists(self.DIR):
            os.mkdir(self.DIR)

        with self._PROC_LOCK:
            if self.is_running():
                raise ServerAlreadyRunningError('Server is already running')

            if not self.jar:
                raise ValueError('Jar not specified')

            # Ensure jar path exists
            jarpath = self.jarpath()
            if not os.path.exists(jarpath):
                raise FileNotFoundError('File not found: ' + jarpath)

            # EULA has to be agreed to otherwise server won't start.
            self._agree_eula()

            # Start process.
            command = 'java %s -jar %s nogui' % (jvm_params, self.jar)
            self._proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=self.DIR)

            # Start threads.
            self._start_console_thread()
            self._start_watchdog_thread()
            self._notify_status_change()
            self._start_time = datetime.datetime.now()

    def stop(self):
        """
        Stops the server.

        It will first try to stop the server gracefully with a SIGTERM, but if the server does not close within
        _SIGTERM_WAIT_SECONDS seconds, the server process will be forcefully terminated.

        This method notifies a status change.

        :raises ServerNotRunningError: if the server is not running
        """
        with self._PROC_LOCK:
            status = self.status()

            if status == ServerStatus.RUNNING:
                _LOGGER.info('Waiting at most %s seconds for server to shut down...' % _SIGTERM_WAIT_SECONDS)
                self._proc.send_signal(signal.SIGTERM)
                self._proc.wait(_SIGTERM_WAIT_SECONDS)

                return_code = self._proc.poll()

                if return_code is None:
                    _LOGGER.warning('Server SIGTERM timed out; terminating forcefully.')
                    self._proc.terminate()

            elif status == ServerStatus.CLOSED:
                _LOGGER.info('Server process was referenced, but it was already closed. Discarding reference.')

            else:
                assert status == ServerStatus.DISABLED
                raise ServerNotRunningError('Server already stopped')

            self._proc = None

        _LOGGER.info('Server process closed.')
        self._notify_status_change()
        self._start_time = None

    def is_running(self):
        return self.status() == ServerStatus.RUNNING

    def uptime(self):
        """
        :return int or None: The uptime of the server in seconds.
        """
        if self._start_time is None:
            return None
        now = datetime.datetime.now()
        delta = now - self._start_time
        return _timedelta_to_seconds(delta)

    def status(self):
        """
        :returns ServerStatus:
            ServerStatus.RUNNING: If server process is referenced and running
            ServerStatus.CLOSED: If server process is referenced but has return code
            ServerStatus.DISABLED: If server process is not referenced
        """
        with self._PROC_LOCK:
            if self._proc is None:
                return ServerStatus.DISABLED
            return_code = self._proc.poll()
            if return_code is None:
                return ServerStatus.RUNNING
            return ServerStatus.CLOSED

    def locate_server_file_path(self):
        """
        Locates the server executable .jar file to be ran by MCAdmin.

        The method will look for any files inside the server directory that are named `minecraft_server-<version>.jar`.

        :raise FileNotFoundError: if no server executables were found.
        :raise TooManyMatchesError: if more than one server executable was found.
        :return: The filename of the server executable.
        """
        matches = glob.glob(os.path.join(self.DIR, 'minecraft_server-*.jar'))
        if len(matches) == 0:
            raise FileNotFoundError(
                'Did not find a server file in directory %s/ (abspath: %s)' % (self.DIR, os.path.abspath(self.DIR)))
        if len(matches) > 1:
            raise TooManyMatchesError('Found more than one server executable in %s: %s' % (self.DIR, str(matches)))
        return os.path.basename(matches[0])

    def eulapath(self):
        return os.path.join(self.DIR, _EULA_TXT)

    def jarpath(self):
        return os.path.join(self.DIR, self.jar)

    def input_line(self, text):
        """
        Sends an input to the server process.

        :param text: Input to send
        :raise ServerNotRunningError: if the server is not running
        """
        with self._PROC_LOCK:
            self._require_server()
            if isinstance(text, str):
                text = text.encode()
            if not text.endswith(b'\n'):
                text += b'\n'
            _LOGGER.debug('Input: ' + str(text))
            self._proc.stdin.write(text)
            self._proc.stdin.flush()

    def _download_latest_vanilla_server(self):
        """
        Downloads the latest vanilla server from the internet and writes the file to the server directory.
        The filename will be the full name of the version.

        :returns str: Name of the file
        :raises IOError: If download failed after _MAX_DOWNLOAD_ATTEMPTS attempts
        """
        version, full_name, link = SERVER_LIST.latest_stable_version()
        _LOGGER.info('Downloading vanilla %s server executable from %s...' % (version, link))
        self._download(link, full_name)
        return full_name

    def _start_console_thread(self):
        """
        Starts the console thread.
        """

        def _console_worker():
            """
            Will read the output from the server process constantly until the server is stopped. It will add the output
            lines to the `self.console_output` deque and notify self.OUTPUT_UPDATE that the console was updated.
            """
            while self.is_running():

                # This ugly hack is required because I needed an atomic comparison, so that the code wouldn't try to
                # access the `proc` variable if it had changed by that point. On top of that, a lock for `proc` should
                # not be acquired here because `proc.stdout.readline()` is blocking.

                # Line being _set to none indicates that the process is closed.
                line = self._proc.stdout.readline() \
                    if self._proc is not None and self._proc.poll() is None \
                    else None
                if line is None:
                    break

                if line != b'':  # Sometimes it reads this and I don't want it
                    encoded = line.decode('utf-8')
                    self.console_output.append(encoded)
                    _LOGGER.debug(encoded)

                    with self.OUTPUT_UPDATE:
                        self.OUTPUT_UPDATE.notify_all()

        threading.Thread(target=_console_worker).start()

    def _start_watchdog_thread(self):
        """
        Starts the watchdog thread.
        """

        def _watchdog_worker():
            """
            Will call the stop procedure when the server process closes.
            """
            while self._proc is not None:
                if self.status() == ServerStatus.CLOSED:
                    _LOGGER.debug('[Watchdog] Process is closed; calling stop()')
                    self.stop()
                time.sleep(1)
            _LOGGER.debug('[Watchdog] Quit')

        threading.Thread(target=_watchdog_worker).start()

    def _notify_status_change(self):
        """
        Notifies all threads waiting on the self.STATUS_CHANGE Condition.
        """
        with self.STATUS_CHANGE:
            self.STATUS_CHANGE.notify_all()

    def _on_program_exit(self):
        """
        Close the server before exiting the Python interpreter.
        """
        if self.is_running():
            _LOGGER.info('Python is exiting: terminating server process.')
            self.stop()

    def _download(self, link, dest_name):
        """
        Downloads a file to the server directory.

        :param link: Link to download
        :param dest_name: Destination name of the file
        :raises IOError: If download failed after _MAX_DOWNLOAD_ATTEMPTS attempts
        """
        for attempt in range(_MAX_DOWNLOAD_ATTEMPTS):
            try:
                response = requests.get(link)
                write_to = os.path.join(os.path.abspath(self.DIR), dest_name)
                _LOGGER.info('Done. Writing to %s ...' % write_to)
                with open(write_to, 'wb') as f:
                    f.write(response.content)
                return
            except IOError as e:
                _LOGGER.error('Could not download server executable. Error: [%s] %s' % (
                    str(e), '... Retrying' if attempt + 1 < _MAX_DOWNLOAD_ATTEMPTS else ''))
        raise IOError('Failed to download server executable after %s attempts.' % _MAX_DOWNLOAD_ATTEMPTS)

    def _agree_eula(self):
        """
        Creates an `eula.txt` file inside the server directory.
        Writes the text required to agree to the Mojang EULA to the file.
        """
        with open(self.eulapath(), 'w') as f:
            f.write(
                '#By changing the setting below to TRUE you are indicating your agreement to our EULA '
                '(https://account.mojang.com/documents/minecraft_eula)\n'
                '#Mon Mar 20 21:15:37 PDT 2017\n'
                'eula=true\n')

    def _require_server(self):
        """
        :raise ServerNotRunningError: if the server is not running
        """
        if not self.is_running():
            raise ServerNotRunningError('Server needs to be running to do this')


_SERVER_DIR = 'server_files'
if not os.path.exists(_SERVER_DIR):
    os.mkdir(_SERVER_DIR)
SERVER = Server(_SERVER_DIR)

# Register the _on_program_exit function to be ran before the Python interpreter quits.
# noinspection PyProtectedMember
atexit.register(SERVER._on_program_exit)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    SERVER.start()
    print('sleep')
    time.sleep(30)
    print('end sleep')
    SERVER.stop()

    import shutil

    shutil.rmtree(SERVER.DIR)
    SERVER_LIST.delete()

    # noinspection PyProtectedMember
    assert SERVER._proc is None
