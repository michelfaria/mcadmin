"""
This module concerns I/O operations on the server.properties file of Minecraft Server.
"""
import json
import os

import yaml

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

    def __init__(self, filepath):
        """
        :param str filepath: Path to the file
        :raises OSError: If the file path is a directory
        """
        if os.path.isdir(filepath):
            raise OSError('Got directory path but expected a file path: ' + filepath)
        self._filepath = filepath

    def exists(self):
        """
        :return: True if the file exists.
        """
        return os.path.exists(self._filepath)

    def read(self):
        """
        :return: The content of the file.
        :raises FileNotFoundError: If the file does not exist
        """
        with open(self._filepath, 'r') as f:
            return f.read()

    def write(self, content):
        """
        Writes content to the file.
        :raises FileNotFoundError: If the file does not exist
        """
        with open(self._filepath, 'w') as f:
            f.write(content)

    def delete(self):
        """
        Deletes the file.
        :raises FileNotFoundError: If the file does not exist
        """
        os.remove(self._filepath)

    def reads(self):
        """
        Reads the file. If the file does not exist, returns an empty string.
        :return str: Content
        """
        if not self.exists():
            return ''
        return self.read()


class JsonFileIO(FileIO):
    """
    Perform I/O operations on JSON files with automatic serialization and deserialization of JSON objects.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self):
        """
        Reads JSON content from the file and returns the parsed content.
        :return dict:
        :raises FileNotFoundError: If the file does not exist
        """
        data = super().read()
        return json.loads(data)

    def write(self, o):
        """
        Writes an object to a JSON file.
        :param o: Object
        """
        parsed = json.dumps(o, indent=4)
        return super().write(parsed)

    def reads(self):
        """
        :returns: an empty dictionary if the file doesn't exist. Otherwise it returns the parsed content.
        """
        if not self.exists():
            return dict()
        return self.read()


class JsonListFileIO(JsonFileIO):
    """
    For the JSON files that have list root elements.
    """

    def reads(self):
        if not self.exists():
            return list()
        return self.read()


class YamlFileIO(FileIO):
    """
    Perform I/O operations on YAML files with automatic serialization and deserialization of YAML objects.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self):
        """
        Reads YAML data from the file and returns its parsed content.
        :return dict: The parsed data
        :raises FileNotFoundError: If the file does not exist
        :raises ParserError: If YAML fails to parse
        """
        data = super().read()
        return yaml.safe_load(data)

    def write(self, o):
        """
        Writes an object to a YAML file.
        :param o: Object to write
        :raises FileNotFoundError: If the file does not exist
        """
        parsed = yaml.safe_dump(o)
        return super().write(parsed)

    def reads(self):
        """
        Reads the file. If the file does not exist, returns an empty dict.
        :return dict: Content
        """
        if not self.exists():
            return dict()
        return self.read()
