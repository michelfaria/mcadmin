# mcadmin/io/server_properties.py
"""
This module concerns I/O operations on the server.properties file of Minecraft Server.
"""
import os

from mcadmin.server.server import SERVER_DIR

FILEPATH = os.path.join(SERVER_DIR, 'server.properties')


def read():
    """
    :return: The content of the server.properties file.
    :raises IOError: if the file does not exist
    """
    with open(FILEPATH, 'r') as f:
        return f.read()


def write(content):
    with open(FILEPATH, 'w') as f:
        f.write(content)
