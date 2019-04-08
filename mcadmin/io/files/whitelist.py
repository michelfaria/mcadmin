import os

from mcadmin.io.files.files import EntryConflictError, EntryNotFoundError, JsonListFileIO
from mcadmin.io.server.server import SERVER

_FILEPATH = os.path.join(SERVER.DIR, 'whitelist.json')
_UUID = 'uuid'
_NAME = 'name'


class _WhitelistFileIO(JsonListFileIO):

    def __init__(self):
        super().__init__(_FILEPATH)

    def add(self, username, uuid):
        """
        Add a user to the whitelist.

        :param str username: Name of the user
        :param str uuid: UUID of the user

        :raises EntryConflictError: If an entry of with that username/uuid already exists
        """
        list_ = self.reads()

        for x in list_:
            if x[_NAME] == username:
                raise EntryConflictError('An entry with name %s already exists' % username)
            elif x[_UUID] == uuid:
                raise EntryConflictError('An entry with UUID %s already exists' % uuid)

        list_.append({
            _UUID: uuid,
            _NAME: username
        })
        self.write(list_)

    def remove(self, name):
        """
        Removes a name from the whitelist.

        :param str name: Name to remove

        :raises EntryNotFoundError: If an entry by the given name does not exist
        """
        list_ = self.reads()

        found = False
        for i, x in enumerate(list_):
            if x[_NAME] == name:
                found = True
                del list_[i]
                break

        if not found:
            raise EntryNotFoundError('Not found in whitelist: %s' % name)

        self.write(list_)


WHITELIST = _WhitelistFileIO()
