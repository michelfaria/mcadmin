import atexit
import configparser

_CONFIG_PATH = 'config.ini'
SECTION_MAIN = 'MAIN'

USE_SERVER_JAR = 'use_server_jar'

CONFIG = configparser.ConfigParser()
CONFIG[SECTION_MAIN] = {
    USE_SERVER_JAR: ''
}
CONFIG.read(_CONFIG_PATH)


# Save when exiting
def exit_handler():
    print('EXITINGGGGGGGGGGGGGGG')
    with open(_CONFIG_PATH, 'w') as f:
        CONFIG.write(f)

print('yooooooooooooooooooooo')
atexit.register(exit_handler)
