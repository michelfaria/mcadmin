import atexit
import configparser
import logging

_LOGGER = logging.getLogger(__name__)

_CONFIG_PATH = 'config.ini'
SECTION_MAIN = 'MAIN'

USE_SERVER_JAR = 'use_server_jar'

CONFIG = configparser.ConfigParser()
CONFIG[SECTION_MAIN] = {
    USE_SERVER_JAR: ''
}
CONFIG.read(_CONFIG_PATH)

_LOGGER.debug('Config module loaded')


# Save when exiting
def exit_handler():
    _LOGGER.debug('Config exit handler called')
    with open(_CONFIG_PATH, 'w') as f:
        CONFIG.write(f)


atexit.register(exit_handler)
