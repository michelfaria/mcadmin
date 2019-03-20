# mcadmin/server/jarentries.py

import os
import re
from functools import wraps
from pprint import pprint

import lxml.html
import requests
import yaml

filename = 'server_list.yml'


def _update_file_if_not_exists(f):
    """
    JarList functions decorated with this function will have their server
    list updated if the list file is no present.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not file_exists():
            update()
        return f(*args, **kwargs)

    return wrapper


def update():
    print('Downloading Minecraft server jars list')
    page = requests.get('https://mcversions.net/')
    print('Got Minecraft Servers list, length: %s' % len(page.text))

    tree = lxml.html.fromstring(page.text)
    d = {x.get('download'): x.get('href') for x in tree.cssselect('a.btn.server')}

    print('Writing to ' + filename)
    with open(filename, 'w') as f:
        yaml.dump(d, f, default_flow_style=False)
    print('Done downloading')


def file_exists():
    return os.path.isfile(filename)


@_update_file_if_not_exists
def load():
    with open(filename, 'r') as f:
        return yaml.safe_load(f)


@_update_file_if_not_exists
def versions():
    stable = []
    snapshot = []
    for full_name, link in load().items():
        version = full_name.split('-', 1)[1].rsplit('.', 1)[0]
        if re.fullmatch(r'[0-9.]+', version):
            stable.append((version, full_name, link))
        else:
            snapshot.append((version, full_name, link))

    stable.sort(key=lambda x: [int(y) for y in x[0].split('.')], reverse=True)
    return {
        'stable': stable,
        'snapshot': snapshot
    }


def latest_stable_ver():
    return versions()['stable'][0]


if __name__ == '__main__':
    pprint(latest_stable_ver())
