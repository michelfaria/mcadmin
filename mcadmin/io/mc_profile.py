"""
Utility for getting information about a Minecraft user
"""
import json
from urllib.parse import urljoin

import requests

from mcadmin.exception import PublicError

ID = 'id'
NAME = 'name'
MOJANG_USER_API = 'https://api.mojang.com/users/profiles/minecraft/'


class ProfileAPIError(PublicError):
    """
    Raised when the Mojang profile API responds erroneously.
    """


class UUIDNotFoundError(PublicError):
    """
    Raised when the UUID of a looked-up user was not found.
    """


def _format_mojang_uuid(uuid_):
    """
    Formats a non-hyphenated UUID into a whitelist-compatible UUID

    :param str uuid_: uuid to format
    :return str: formatted uuid

    Example:
    >>> _format_mojang_uuid('1449a8a244d940ebacf551b88ae95dee')
    '1449a8a2-44d9-40eb-acf5-51b88ae95dee'

    Must have 32 characters:
    >>> _format_mojang_uuid('1')
    Traceback (most recent call last):
        ...
    ValueError: Expected UUID to have 32 characters
    """
    if len(uuid_) != 32:
        raise ValueError('Expected UUID to have 32 characters')
    return uuid_[:8] + '-' + uuid_[8:12] + '-' + uuid_[12:16] + '-' + uuid_[16:20] + '-' + uuid_[20:]


def uuid(username):
    """
    Returns the UUID of a Minecraft username.

    :param str username: Username to look up the UUID for
    :return str: UUID of the user

    :raises ProfileAPIError: If the Mojang API responds erroneously
    :raises UUIDNotFoundError: If UUID for username was not found
    """
    response = requests.get(urljoin(MOJANG_USER_API, username))

    if response.status_code is 204:
        raise UUIDNotFoundError('No UUID found for %s' % username)

    elif response.status_code is 200:
        response = json.loads(response.content)

        if NAME not in response or ID not in response:
            raise ProfileAPIError('Received erroneous response from Mojang profile API: %s' % response.content)
        elif response[NAME].casefold() != username.casefold():
            raise ProfileAPIError(
                'Mojang API may be problematic: Requested profile for %s but got username %s. The entire response '
                'was: %s' % (username, response[NAME], response.content))
        else:
            return _format_mojang_uuid(response[ID])

    else:
        raise ValueError('Got response status %d but expected 200' % response.status_code)
