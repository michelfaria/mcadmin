import os

from mcadmin.io.files.files import FileIO
from mcadmin.io.server.server import SERVER_DIR

_FILEPATH = os.path.join(SERVER_DIR, 'server.properties')
SERVER_PROPERTIES = FileIO(_FILEPATH)
