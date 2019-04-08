"""
This module concerns I/O operations on the server.properties file of Minecraft Server.
"""
import json
import os

from mcadmin.exception import PublicError


class EntryConflictError(PublicError):
    """
    Raised when it is made an attempt to insert a duplicate element into an entry set where duplicates are not allowed.
    """


class EntryNotFoundError(PublicError):
    """
    Raised when it is made an attempt to operate on an non-existing entry of the whitelist.
    """


class FileIO:
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


class JsonIO(FileIO):
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


