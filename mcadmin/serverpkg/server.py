import glob
import os
import time
from subprocess import Popen, PIPE, STDOUT

import requests

from mcadmin.serverpkg import jarentries

SERVER_DIR = 'server_files'
MAX_DOWNLOAD_ATTEMPTS = 2

# create server dir if it does not exist
if not os.path.exists(SERVER_DIR):
    os.mkdir(SERVER_DIR)


class TooManyMatchesError(Exception):
    """
    For when a lookup returns more than one match when just one is expected.
    """
    pass


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

    print('Downloading server from %s ...' % link)
    response = requests.get(link)
    write_to = os.path.join(os.path.abspath(SERVER_DIR), full_name)

    print('Downloaded. Writing to %s ...' % write_to)
    with open(write_to, 'wb') as f:
        f.write(response.content)
    return full_name


def _agree_eula():
    eula_path = os.path.join(SERVER_DIR, 'eula.txt')
    with open(eula_path, 'w') as f:
        f.write(
            '#By changing the setting below to TRUE you are indicating your agreement to our EULA '
            '(https://account.mojang.com/documents/minecraft_eula)\n'
            '#Mon Mar 20 21:15:37 PDT 2017\n'
            'eula=true\n')


def start(server_jar_name=None, jvm_params=''):
    # if a server jar name was specified,
    # it will be used instead of the latest version
    if server_jar_name:
        path = os.path.join(SERVER_DIR, server_jar_name)
        if not os.path.exists(path):
            raise FileNotFoundError('File %s not found' % os.path.abspath(path))
    else:
        # server file not specified
        # download latest stable version
        success = False
        for _ in range(MAX_DOWNLOAD_ATTEMPTS):
            try:
                server_jar_name = _locate_server_file_name()
                success = True
                break
            except FileNotFoundError:
                print('No server file found; will attempt to download latest server file')
                try:
                    server_jar_name = _download_latest_server()
                    success = True
                    break
                except IOError as ex:
                    print('Download failed: ' + ex)
        if not success:
            raise IOError('Server start failed: Could not download latest server jar')
    assert server_jar_name

    # eula has to be agreed to otherwise server won't start
    _agree_eula()

    command = 'java %s -jar %s nogui' % (jvm_params, server_jar_name)
    proc = Popen(command, stdout=PIPE, cwd=SERVER_DIR)

    while True:
        line = proc.stdout.readline()
        if len(line) > 0:
            print(line)


if __name__ == '__main__':
    start()
