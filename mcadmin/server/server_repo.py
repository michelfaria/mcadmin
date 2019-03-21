# mcadmin/server/server_repo.py

import os
import re
from functools import wraps
from pprint import pprint

import logging
import lxml.html
import requests
import yaml

LOGGER = logging.getLogger(__name__)
FILENAME = 'server_list.yml'


def _update_repo_if_not_exists(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not repo_exists():
            update()
        return f(*args, **kwargs)

    return wrapper


def update():
    LOGGER.info('Updating Minecraft server executable link repository...')
    page = requests.get('https://mcversions.net/')
    LOGGER.info('Got list, length: %s.' % len(page.text))

    tree = lxml.html.fromstring(page.text)
    d = {x.get('download'): x.get('href') for x in tree.cssselect('a.btn.server')}

    LOGGER.debug('Writing to ' + FILENAME)
    with open(FILENAME, 'w') as f:
        yaml.dump(d, f, default_flow_style=False)
    LOGGER.info('Server executable repository updated!')


def repo_exists():
    return os.path.isfile(FILENAME)


@_update_repo_if_not_exists
def load():
    with open(FILENAME, 'r') as f:
        return yaml.safe_load(f)


@_update_repo_if_not_exists
def versions():
    stable = []
    snapshot = []
    for full_name, link in load().items():
        version = full_name.split('-', 1)[1].rsplit('.', 1)[0]
        if re.fullmatch(r'[0-9.]+', version):
            stable.append((version, full_name, link))
        else:
            snapshot.append((version, full_name, link))

    # Sort the list of stable versions in descending order
    # lambda x :: x => tuple(version, full_name, link) :: x -> [int]
    stable.sort(key=lambda x: [int(y) for y in x[0].split('.')], reverse=True)

    return {
        'stable': stable,
        'snapshot': snapshot
    }


def latest_stable_ver():
    return versions()['stable'][0]


if __name__ == '__main__':
    pprint(latest_stable_ver())
