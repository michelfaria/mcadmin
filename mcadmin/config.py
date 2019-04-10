import logging
from configparser import ConfigParser

_LOGGER = logging.getLogger(__name__)
_CONFIG_PATH = 'config.ini'

# Sections
_SECT_MAIN = 'MAIN'

# Fields
# [MAIN]
_F_USE_JAR = 'use_server_jar'


class Config:

    def __init__(self, path):
        self._path = path
        self._config = ConfigParser()
        self._config[_SECT_MAIN] = {
            _F_USE_JAR: ''
        }

    def load(self):
        _LOGGER.debug('Config loaded')
        self._config.read(self._path)

    def save(self):
        _LOGGER.debug('Writing config')
        with open(self._path, 'w') as f:
            self._config.write(f)

    def _set(self, section, field, value, save=True):
        _LOGGER.debug('_set: section=%s, field=%s, value=%s, save=%s' % (section, field, value, save))
        self._config[section][field] = value
        if save:
            self.save()

    def set_use_jar(self, value, **kwargs):
        self._set(_SECT_MAIN, _F_USE_JAR, value, **kwargs)

    def get_use_jar(self):
        return self._config[_SECT_MAIN][_F_USE_JAR]


CONFIG = Config(_CONFIG_PATH)
CONFIG.load()
