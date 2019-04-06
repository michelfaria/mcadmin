"""
This module concerns I/O operations on the server.properties file of Minecraft Server.
"""
import os

from mcadmin.server.server import SERVER_DIR

SERVER_PROPERTIES_FILEPATH = os.path.join(SERVER_DIR, 'server.properties')
WHITELIST_FILEPATH = os.path.join(SERVER_DIR, 'whitelist.json')
BANNED_PLAYERS_FILEPATH = os.path.join(SERVER_DIR, 'banned-players.json')
BANNED_IPS_FILEPATH = os.path.join(SERVER_DIR, 'banned-ips.json')


class _FileIO:
    """
    Utility class for performing basic operations on files.
    """

    def __init__(self, filename):
        self._filename = filename

    def exists(self):
        """
        :return: True if the file exists.
        """
        return os.path.exists(self._filename)

    def read(self):
        """
        :return: The content of the file.
        :raises IOError: if the file does not exist
        """
        with open(self._filename, 'r') as f:
            return f.read()

    def write(self, content):
        with open(self._filename, 'w') as f:
            f.write(content)


SERVER_PROPERTIES_IO = _FileIO(SERVER_PROPERTIES_FILEPATH)
WHITELIST_IO = _FileIO(WHITELIST_FILEPATH)
BANNED_PLAYERS_IO = _FileIO(BANNED_PLAYERS_FILEPATH)
BANNED_IPS_IO = _FileIO(BANNED_IPS_FILEPATH)
