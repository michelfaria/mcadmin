"""
Utility for getting information about a Minecraft user
"""
import json
from urllib.parse import urljoin

import requests

MOJANG_USER_API = 'https://api.mojang.com/users/profiles/minecraft/'


class ProfileAPIError(BaseException):
    """
    Raise when the Mojang profile API responds erroneously.
    """
    pass


def uuid(username):
    """
    Returns the UUID of a Minecraft username.

    :param username: Username to look up the UUID for
    :type username: str
    :return: UUID, or None if the username was not found
    :rtype: str | None

    :raise ProfileAPIError: If the Mojang API responds erroneously
    """
    response = requests.get(urljoin(MOJANG_USER_API, username))

    if response.status_code is 200:
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
        return None
