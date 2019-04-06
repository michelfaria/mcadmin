"""
This module concerns I/O operations on the server.properties file of Minecraft Server.
"""
import json
import os

from mcadmin.server.server import SERVER_DIR

SERVER_PROPERTIES_FILEPATH = os.path.join(SERVER_DIR, 'server.properties')
WHITELIST_FILEPATH = os.path.join(SERVER_DIR, 'whitelist.json')
BANNED_PLAYERS_FILEPATH = os.path.join(SERVER_DIR, 'banned-players.json')
BANNED_IPS_FILEPATH = os.path.join(SERVER_DIR, 'banned-ips.json')


class EntryNotFound(Exception):
    """
    Raised when it is made an attempt to operate on an non-existing entry of the whitelist.
    """
    pass


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


class _JsonIO(_FileIO):
    """
    Perform I/O operations on JSON files with automatic serialization and deserialization of JSON objects.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self):
        data_str = super().read()
        return json.loads(data_str)

    def write(self, obj):
        parsed = json.dumps(obj, indent=4)
        return super().write(parsed)


class _WhitelistIO(_JsonIO):

    def __init__(self):
        super().__init__(WHITELIST_FILEPATH)

    def add(self, name, uuid):
        """
        Add a user to the whitelist.

        :param name: Name of the user
        :type name: str
        :param uuid: UUID of the user
        :type uuid: str
        """
        list_ = self.read()
        list_.append({
            'uuid': uuid,
            'name': name
        })
        self.write(list_)

    def remove(self, name):
        """
        Removes a name from the whitelist.

        :param name: Name to remove
        :rtype name: str
        :raises EntryNotFound: If an entry by the given name does not exist
        """
        list_ = self.read()

        found = False
        for i, x in enumerate(list_):
            if x['name'] == name:
                found = True
                del list_[i]
                break

        if not found:
            raise EntryNotFound('Not found in whitelist: %s' % name)

        self.write(list_)


SERVER_PROPERTIES_FILE = _FileIO(SERVER_PROPERTIES_FILEPATH)
BANNED_PLAYERS_FILE = _FileIO(BANNED_PLAYERS_FILEPATH)
BANNED_IPS_FILE = _FileIO(BANNED_IPS_FILEPATH)
WHITELIST_FILE = _WhitelistIO()
