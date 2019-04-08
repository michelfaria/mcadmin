import os

from mcadmin.io.files.files import FileIO
from mcadmin.server.server import SERVER_DIR

SERVER_PROPERTIES_FILEPATH = os.path.join(SERVER_DIR, 'server.properties')
server_properties_io = FileIO(SERVER_PROPERTIES_FILEPATH)
