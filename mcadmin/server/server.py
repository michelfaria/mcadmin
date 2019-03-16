import subprocess
import glob

SERVER_DIR = 'server_files'


def locate_server_executable():
    matches = glob.glob('%s/*-server.jar' % SERVER_DIR)
    if len(matches) == 0:
        raise IOError('Found no server files in %s/' % SERVER_DIR)
    elif len(matches) > 1:
        raise IOError('Found more than one server file in %s: %s' % (SERVER_DIR, str(matches)))
    else:
        return matches


def start():
    print('Found server: ' + str(locate_server_executable()))


if __name__ == '__main__':
    start()
