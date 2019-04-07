"""
Utility for getting information about a Minecraft user
"""
import json
from urllib.parse import urljoin

import requests

from mcadmin.exception import PublicError

MOJANG_USER_API = 'https://api.mojang.com/users/profiles/minecraft/'


class ProfileAPIError(PublicError):
    """
    Raised when the Mojang profile API responds erroneously.
    """


class UUIDNotFoundError(PublicError):
    """
    Raised when the UUID of a looked-up user was not found.
    """


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
        obj = json.loads(response.content)
        if 'name' not in obj or 'id' not in obj:
            raise ProfileAPIError('Received erroneous response from Mojang profile API: %s' % response.content)
        elif obj['name'].lower() != username:
            raise ProfileAPIError(
                'Mojang API may be problematic: Requested profile for %s but got username %s. The entire response '
                'was: %s' % (username, obj['name'], response.content))
        else:
            return obj['id']

    else:
        raise ValueError('Got response status %d but expected 200' % response.status_code)
