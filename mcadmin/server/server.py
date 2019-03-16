import glob
from pprint import pprint
import os
from subprocess import Popen, PIPE, STDOUT

SERVER_DIR = 'server_files'


class TooManyMatchesError(Exception):
    """
    For when a lookup returns more than one match when just one is expected.
    """
    pass


def locate_server_file():
    matches = glob.glob('%s/*-server.jar' % SERVER_DIR)
    if len(matches) == 0:
        raise FileNotFoundError(
            'Did not find a server file in directory %s/ (abspath: %s)' % (SERVER_DIR, os.path.abspath(SERVER_DIR)))
    if len(matches) > 1:
        raise TooManyMatchesError('Found more than one server file in %s: %s' % (SERVER_DIR, str(matches)))
    return matches


def start(java_settings=''):
    server_file = None
    try:
        server_file = locate_server_file()
    except FileNotFoundError as ex:
        print('No server file found; downloading latest')

        return

    process = Popen('java %s -jar %s' % (java_settings, server_file),
                    stdout=STDOUT, stdin=PIPE, stderr=STDOUT,
                    shell=True, cwd=os.path.dirname(server_file))


if __name__ == '__main__':
    start()
