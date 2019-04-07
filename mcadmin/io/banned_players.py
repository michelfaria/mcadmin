import os

from mcadmin.io.files import JsonIO, EntryConflictError
from mcadmin.server.server import SERVER_DIR
from mcadmin.io.mc_profile import mc_uuid
from datetime import datetime

BANNED_PLAYERS_FILEPATH = os.path.join(SERVER_DIR, 'banned-players.json')

UUID = 'uuid'
NAME = 'name'
CREATED = 'created'
SOURCE = 'source'
EXPIRES = 'expires'
REASON = 'reason'

FOREVER = 'forever'
DEFAULT_BAN_REASON = 'Banned by an operator.'


def mojang_time_format(dt):
    """
    Formats datetime to Mojang's format.
    :param datetime dt: datetime

    >>> mojang_time_format(datetime(2010, 4, 25, 23, 43, 20))
    '2010-04-25 23:43:20 +0000'
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S +0000')


class BannedPlayersIO(JsonIO):
    def __init__(self):
        super().__init__(BANNED_PLAYERS_FILEPATH)

    def ban(self, name, reason=None):
        """
        Bans a player.

        :param str name: Name of the user to ban
        :param str reason: Reason for the ban

        :raises EntryConflictError: If the player is already banned
        :raises ProfileAPIError: If the Mojang API responds erroneously
        :raises UUIDNotFoundError: If UUID for username was not found
        """
        list_ = self.read()

        if self._is_banned(name, list_):
            raise EntryConflictError('Player %s is already banned.', name)

        uuid = mc_uuid(name)
        new_entry = {
            UUID: uuid,
            NAME: name,
            CREATED: mojang_time_format(datetime.now()),
            SOURCE: 'MCAdmin',
            EXPIRES: FOREVER,
            REASON: DEFAULT_BAN_REASON if reason is None else reason
        }

        list_.append(new_entry)
        self.write(list_)

    # noinspection PyProtectedMember
    def _is_banned(self, name, list_=None):
        """
        Returns true if the specified name is contained in the ban list.

        :param name: Name of the person to ban
        :param list_: Ban list to use. Will read list from disk if not specified.
        :return bool: True if the specified name is contained in the ban list.

        >>> o = BannedPlayersIO()
        >>> o._is_banned('john', [{NAME: 'Mack'}, {NAME: 'John'}])
        True

        >>> o = BannedPlayersIO()
        >>> o._is_banned('bob', [{NAME: 'John'}, {NAME: 'Jack'}])
        False
        """
        if list_ is None:
            list_ = self.read()
        return any([e for e in list_ if e[NAME].casefold() == name.casefold()])


banned_players_io = BannedPlayersIO()
