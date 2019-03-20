# mcadmin/server/server.py

import threading
import atexit
import glob
import logging
import os
import signal
import time
import collections
from subprocess import Popen, PIPE

import requests

from mcadmin.server import jarentries

LOGGER = logging.getLogger(__name__)
SERVER_DIR = 'server_files'
MAX_DOWNLOAD_ATTEMPTS = 2
SIGTERM_WAIT_SECONDS = 30
CONSOLE_OUTPUT_MAX_LINES = 100

# console output buffer that will be sent to the client when they open the console page.
console_output = collections.deque(maxlen=CONSOLE_OUTPUT_MAX_LINES)

# java server process handle
proc = None  # type: Popen

# thread that updates console_output with new lines
console_thread = None  # type: threading.Thread

# create server dir if it does not exist
if not os.path.exists(SERVER_DIR):
    os.mkdir(SERVER_DIR)


class TooManyMatchesError(Exception):
    """
    For when a lookup returns more than one match when just one is expected.
    """
    pass


def is_server_running():
    return proc is not None and proc.poll() is None


def stop():
    global proc
    global console_thread

    if not is_server_running():
        raise ValueError('Server is not running: no process reference')
    return_code = proc.poll()
    if return_code is not None:
        raise ValueError('Server is not running: no return code')

    LOGGER.info('Waiting at most %s seconds for server to shut down ...' % SIGTERM_WAIT_SECONDS)
    proc.send_signal(signal.SIGTERM)
    proc.wait(SIGTERM_WAIT_SECONDS)

    assert not console_thread.is_alive()

    return_code = proc.poll()

    if return_code is None:
        LOGGER.warning('Server SIGTERM timed out; terminating forcefully')
        proc.terminate()
    else:
        LOGGER.info('Server process closed')

    proc = None
    console_thread = None
    return return_code


def _on_program_exit():
    if is_server_running():
        LOGGER.info('Python is exiting: terminating server process')
        stop()


atexit.register(_on_program_exit)


def _locate_server_file_name():
    matches = glob.glob(os.path.join(SERVER_DIR, 'minecraft_server-*.jar'))
    if len(matches) == 0:
        raise FileNotFoundError(
            'Did not find a server file in directory %s/ (abspath: %s)' % (SERVER_DIR, os.path.abspath(SERVER_DIR)))
    if len(matches) > 1:
        raise TooManyMatchesError('Found more than one server file in %s: %s' % (SERVER_DIR, str(matches)))
    return os.path.basename(matches[0])


def _download_latest_server():
    version, full_name, link = jarentries.latest_stable_ver()

    for attempt in range(MAX_DOWNLOAD_ATTEMPTS):
        LOGGER.info('Downloading server from %s ...' % link)
        try:
            response = requests.get(link)
            write_to = os.path.join(os.path.abspath(SERVER_DIR), full_name)

            LOGGER.info('Downloaded. Writing to %s ...' % write_to)
            with open(write_to, 'wb') as f:
                f.write(response.content)
            return full_name
        except IOError as e:
            LOGGER.error('Could not download server: [%s] %s' % (
                str(e), '... Retrying' if attempt + 1 < MAX_DOWNLOAD_ATTEMPTS else ''))

    raise IOError('Failed to download server after %s attempts' % MAX_DOWNLOAD_ATTEMPTS)


def _agree_eula():
    eula_path = os.path.join(SERVER_DIR, 'eula.txt')
    with open(eula_path, 'w') as f:
        f.write(
            '#By changing the setting below to TRUE you are indicating your agreement to our EULA '
            '(https://account.mojang.com/documents/minecraft_eula)\n'
            '#Mon Mar 20 21:15:37 PDT 2017\n'
            'eula=true\n')


def start(server_jar_name=None, jvm_params=''):
    global proc

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
            LOGGER.warning('No server file found; will attempt to download latest server file')
            server_jar_name = _download_latest_server()
    assert server_jar_name

    # eula has to be agreed to otherwise server won't start
    _agree_eula()

    command = 'java %s -jar %s nogui' % (jvm_params, server_jar_name)
    proc = Popen(command, stdout=PIPE, stdin=PIPE, stderr=PIPE, cwd=SERVER_DIR)

    _start_console_thread()


def _start_console_thread():
    global console_thread

    if console_thread is not None:
        raise ValueError('Thread already exists')

    console_thread = threading.Thread(target=_console_worker)
    console_thread.start()


def _console_worker():
    while is_server_running():
        assert proc is not None and proc.poll() is None
        line = proc.stdout.readlines()
        if len(line) > 0:
            console_output.append(line)


def input_line(text):
    _require_server()
    proc.stdin.write(text)


def input_lines(lines):
    _require_server()
    proc.stdin.writelines(lines)


def _require_server():
    """
    Raises a ValueError if the server is not running
    """
    if not is_server_running():
        raise ValueError('Server needs to be running to do this')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    start()
    print('sleep')
    time.sleep(30)
    print('end sleep')
    stop()
    import shutil
    shutil.rmtree(SERVER_DIR)
    os.remove(jarentries.filename)
    assert proc is None
