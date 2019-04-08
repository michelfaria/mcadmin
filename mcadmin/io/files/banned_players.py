import os
from datetime import datetime

from mcadmin.io.files.files import EntryConflictError, EntryNotFoundError, JsonListFileIO
from mcadmin.io.mc_profile import mc_uuid
from mcadmin.io.server.server import SERVER

_BANNED_PLAYERS_FILEPATH = os.path.join(SERVER.DIR, 'banned-players.json')
_UUID = 'uuid'
_NAME = 'name'
_CREATED = 'created'
_SOURCE = 'source'
_EXPIRES = 'expires'
_REASON = 'reason'
_FOREVER = 'forever'
_DEFAULT_BAN_REASON = 'Banned by an operator.'


def mojang_time_format(dt):
    """
    Formats datetime to Mojang's format.
    :param datetime dt: datetime

    >>> mojang_time_format(datetime(2010, 4, 25, 23, 43, 20))
    '2010-04-25 23:43:20 +0000'
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S +0000')


class _BannedPlayersFileIO(JsonListFileIO):
    def __init__(self):
        super().__init__(_BANNED_PLAYERS_FILEPATH)

    def ban(self, name, reason=None):
        """
        Bans a player.

        :param str name: Name of the user to ban
        :param str reason: Reason for the ban

        :raises EntryConflictError: If the player is already banned
        :raises ProfileAPIError: If the Mojang API responds erroneously
        :raises UUIDNotFoundError: If UUID for username was not found
        """
        list_ = self.reads()

        if self._is_banned(name, list_):
            raise EntryConflictError('Player %s is already banned.', name)

        uuid = mc_uuid(name)
        new_entry = {
            _UUID: uuid,
            _NAME: name,
            _CREATED: mojang_time_format(datetime.now()),
            _SOURCE: 'MCAdmin',
            _EXPIRES: _FOREVER,
            _REASON: _DEFAULT_BAN_REASON if reason is None or reason == '' else reason
        }

        list_.append(new_entry)
        self.write(list_)

    def pardon(self, name):
        """
        Pardons a user.

        :param str name: Username of the user to pardon.
        :raises EntryNotFoundError: If the player is not found in the ban list
        """
        list_ = self.reads()

        found = False
        for i, e in enumerate(list_):
            if e[_NAME].casefold() == name.casefold():
                found = True
                del list_[i]
                break

        if not found:
            raise EntryNotFoundError('%s not found in the ban list.' % name)

        self.write(list_)

    # noinspection PyProtectedMember
    def _is_banned(self, name, list_=None):
        """
        Returns true if the specified name is contained in the ban list.

        :param name: Name of the person to ban
        :param list_: Ban list to use. Will read list from disk if not specified.
        :return bool: True if the specified name is contained in the ban list.

        >>> o = _BannedPlayersFileIO()
        >>> o._is_banned('john', [{_NAME: 'Mack'}, {_NAME: 'John'}])
        True

        >>> o = _BannedPlayersFileIO()
        >>> o._is_banned('bob', [{_NAME: 'John'}, {_NAME: 'Jack'}])
        False
        """
        if list_ is None:
            list_ = self.reads()
        return any([e for e in list_ if e[_NAME].casefold() == name.casefold()])


BANNED_PLAYERS = _BannedPlayersFileIO()
