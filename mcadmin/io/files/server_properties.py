import os

from mcadmin.io.files.files import FileIO
from mcadmin.io.server.server import SERVER

_FILEPATH = os.path.join(SERVER.DIR, 'server.properties')
SERVER_PROPERTIES = FileIO(_FILEPATH)
