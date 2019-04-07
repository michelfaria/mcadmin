import atexit
import collections
import glob
import logging
import os
import signal
import threading
import time
from enum import Enum
from subprocess import Popen, PIPE

import requests

from mcadmin.server import server_repo

LOGGER = logging.getLogger(__name__)
SERVER_DIR = 'server_files'  # Server files directory
MAX_DOWNLOAD_ATTEMPTS = 2  # Maximum amount of times to try to download a server executable from the internet
SIGTERM_WAIT_SECONDS = 30  # Maximum amount of time to wait for a process to end
CONSOLE_OUTPUT_MAX_LINES = 100  # Maximum amount of lines that there can be inside the console_output deque

# Notified every time the server status change from ON to OFF or vice-versa.
SERVER_STATUS_CHANGE = threading.Condition()
# Notified whenever there is a console output
CONSOLE_OUTPUT_COND = threading.Condition()

# Console output buffer that will be sent to the client when they open the console page
CONSOLE_OUTPUT = collections.deque(maxlen=CONSOLE_OUTPUT_MAX_LINES)

# Java Server Process Handle
proc = None  # type: Popen
PROC_LOCK = threading.RLock()

# Create server files directory if it does not exist.
if not os.path.exists(SERVER_DIR):
    os.mkdir(SERVER_DIR)


class TooManyMatchesError(Exception):
    """
    For when a lookup returns more than one match when just one is expected.
    """
    pass


class ServerAlreadyRunningError(Exception):
    """
    Raised when trying to start the server when it is already running.
    """
    pass


class ServerNotRunningError(Exception):
    """
    Raised when an action that requires a running server is performed without the server running.
    """
    pass


class ServerStatus(Enum):
    """
    Enum for representing server statuses. See is_server_running() for usage.
    """
    RUNNING = 'running'
    CLOSED = 'closed'
    DISABLED = 'disabled'


def server_status():
    """
    :returns ServerStatus:
        ServerStatus.RUNNING: If server process is referenced and running
        ServerStatus.CLOSED: If server process is referenced but has return code
        ServerStatus.DISABLED: If server process is not referenced
    """
    with PROC_LOCK:
        if proc is None:
            return ServerStatus.DISABLED
        return_code = proc.poll()
        if return_code is None:
            return ServerStatus.RUNNING
        return ServerStatus.CLOSED


def is_server_running():
    return server_status() == ServerStatus.RUNNING


def _notify_status_change():
    """
    Notifies all threads waiting on the SERVER_STATUS_CHANGE Condition.
    """
    with SERVER_STATUS_CHANGE:
        SERVER_STATUS_CHANGE.notify_all()


def stop():
    """
    Stops the server.

    It will first try to stop the server gracefully with a SIGTERM, but if the server does not close within
    SIGTERM_WAIT_SECONDS seconds, the server process will be forcefully terminated.

    This method notifies a status change.

    :raises ServerNotRunningError: if the server is not running
    """
    global proc

    with PROC_LOCK:
        status = server_status()

        if status == ServerStatus.RUNNING:
            LOGGER.info('Waiting at most %s seconds for server to shut down...' % SIGTERM_WAIT_SECONDS)
            proc.send_signal(signal.SIGTERM)
            proc.wait(SIGTERM_WAIT_SECONDS)

            return_code = proc.poll()

            if return_code is None:
                LOGGER.warning('Server SIGTERM timed out; terminating forcefully.')
                proc.terminate()

        elif status == ServerStatus.CLOSED:
            LOGGER.info('Server process was referenced, but it was already closed. Discarding reference.')

        else:
            assert status == ServerStatus.DISABLED
            raise ServerNotRunningError('Server already stopped')

        proc = None

    LOGGER.info('Server process closed.')

    _notify_status_change()


def _on_program_exit():
    """
    Close the server before exiting the Python interpreter.
    """
    if is_server_running():
        LOGGER.info('Python is exiting: terminating server process.')
        stop()


# Register the _on_program_exit function to be ran before the Python interpreter quits.
atexit.register(_on_program_exit)


def _locate_server_file_name():
    """
    Locates the server executable .jar file to be ran by MCAdmin.

    The method will look for any files inside the server directory that are named `minecraft_server-<version>.jar`.

    :raise FileNotFoundError: if no server executables were found.
    :raise TooManyMatchesError: if more than one server executable was found.
    :return: The filename of the server executable.
    """
    matches = glob.glob(os.path.join(SERVER_DIR, 'minecraft_server-*.jar'))
    if len(matches) == 0:
        raise FileNotFoundError(
            'Did not find a server file in directory %s/ (abspath: %s)' % (SERVER_DIR, os.path.abspath(SERVER_DIR)))
    if len(matches) > 1:
        raise TooManyMatchesError('Found more than one server executable in %s: %s' % (SERVER_DIR, str(matches)))
    return os.path.basename(matches[0])


def _download_latest_vanilla_server():
    """
    Downloads the latest vanilla server from the internet and writes the file to SERVER_DIR.
    The filename will be the full name of the version.

    :raises IOError: If download failed after MAX_DOWNLOAD_ATTEMPTS attempts
    """
    version, full_name, link = server_repo.latest_stable_ver()

    for attempt in range(MAX_DOWNLOAD_ATTEMPTS):
        LOGGER.info('Downloading vanilla %s server executable from %s...' % (version, link))
        try:
            response = requests.get(link)
            write_to = os.path.join(os.path.abspath(SERVER_DIR), full_name)

            LOGGER.info('Done. Writing to %s ...' % write_to)

            with open(write_to, 'wb') as f:
                f.write(response.content)
            return full_name
        except IOError as e:
            LOGGER.error('Could not download server executable. Error: [%s] %s' % (
                str(e), '... Retrying' if attempt + 1 < MAX_DOWNLOAD_ATTEMPTS else ''))

    raise IOError('Failed to download server executable after %s attempts.' % MAX_DOWNLOAD_ATTEMPTS)


def _agree_eula():
    """
    Creates an `eula.txt` file inside the server directory.
    Writes the text required to agree to the Mojang EULA to the file.
    """
    eula_path = os.path.join(SERVER_DIR, 'eula.txt')
    with open(eula_path, 'w') as f:
        f.write(
            '#By changing the setting below to TRUE you are indicating your agreement to our EULA '
            '(https://account.mojang.com/documents/minecraft_eula)\n'
            '#Mon Mar 20 21:15:37 PDT 2017\n'
            'eula=true\n')


def start(server_jar_name=None, jvm_params=''):
    """
    Starts the server.

    The latest server file will be downloaded automatically if `server_jar_name` was not specified and a server executable
    does not exist inside the server directory.

    This will also start the console thread.
    This method notified a status change.

    :param server_jar_name: The filename of the server to use.
                            If not specified, it will find the server file automatically.
    :param jvm_params:      Parameters used when starting the JVM. Nothing by default.

    :raise ServerAlreadyRunningError: If the server is already running.
    :raise FileNotFoundError:         If `server_jar_name` param was specified but a file by that name was not found
                                      inside the server directory.
    """
    global proc

    with PROC_LOCK:
        if is_server_running():
            raise ServerAlreadyRunningError('Server is already running')

        # if a server jar name was specified,
        # it will be used instead of the latest version
        if server_jar_name:
            path = os.path.join(SERVER_DIR, server_jar_name)
            if not os.path.exists(path):
                raise FileNotFoundError('File %s not found' % os.path.abspath(path))
        else:
            # server file not specified
            # download latest stable version
            try:
                server_jar_name = _locate_server_file_name()
            except FileNotFoundError:
                LOGGER.warning('No server executable found; will attempt to download latest vanilla server.')
                server_jar_name = _download_latest_vanilla_server()
        assert server_jar_name

        # eula has to be agreed to otherwise server won't start
        _agree_eula()

        command = 'java %s -jar %s nogui' % (jvm_params, server_jar_name)
        proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=SERVER_DIR)

        _start_console_thread()
        _start_watchdog_thread()
        _notify_status_change()


def _start_console_thread():
    """
    Starts the console thread and assigns it to the global `console_thread` variable.

    :raise ValueError: if a thread is already referenced by `console_thread`.
    """

    def _console_worker():
        """
        Will read the output from the server process constantly until the server is stopped. It will add the output lines
        to the `console_output` deque and notify CONSOLE_OUTPUT_COND that the console was updated.
        """
        while is_server_running():
            # This ugly hack is required because I needed an atomic comparison, so that the code wouldn't try to
            # access the `proc` variable if it had changed by that point. On top of that, a lock for `proc` should
            # not be acquired here because `proc.stdout.readline()` is blocking.

            # Line being set to none indicates that the process is closed.
            line = proc.stdout.readline() \
                if proc is not None and proc.poll() is None \
                else None
            if line is None:
                break

            if line != b'':  # Sometimes it reads this and I don't want it
                encoded = line.decode('utf-8')
                CONSOLE_OUTPUT.append(encoded)
                LOGGER.debug(encoded)

                with CONSOLE_OUTPUT_COND:
                    CONSOLE_OUTPUT_COND.notify_all()

    threading.Thread(target=_console_worker).start()


def _start_watchdog_thread():
    """
    Starts the watchdog thread and assigns it to the global `watchdog_thread` variable.

    :raise ValueError: If `watchdog_thread` already has an assignment
    """

    def _watchdog_worker():
        """
        Will officially stop the server whenever it sees that the process has ended, until `proc` is de-referenced.
        """
        while proc is not None:
            if server_status() == ServerStatus.CLOSED:
                LOGGER.debug('[Watchdog] Process is closed; calling stop()')
                stop()
            time.sleep(1)
        LOGGER.debug('[Watchdog] Quit')

    threading.Thread(target=_watchdog_worker).start()


def input_line(text):
    """
    Sends an input to the server process.

    :param text: Input to send
    :raise ServerNotRunningError: if the server is not running
    """
    with PROC_LOCK:
        _require_server()
        if isinstance(text, str):
            text = text.encode()
        if not text.endswith(b'\n'):
            text += b'\n'
        LOGGER.debug('Input: ' + str(text))
        proc.stdin.write(text)
        proc.stdin.flush()


def _require_server():
    """
    :raise ServerNotRunningError: if the server is not running
    """
    if not is_server_running():
        raise ServerNotRunningError('Server needs to be running to do this')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    start()
    print('sleep')
    time.sleep(30)
    print('end sleep')
    stop()

    import shutil

    shutil.rmtree(SERVER_DIR)
    os.remove(server_repo.FILENAME)

    assert proc is None
