import os
from functools import wraps

import lxml.html
import requests
import yaml

FILENAME = 'server_list.yml'


class JarList:
    def __init__(self, filename=FILENAME):
        self.filename = filename

    def update(self):
        print('Downloading Minecraft server jars list')
        page = requests.get('https://mcversions.net/')
        print('Got Minecraft Servers list, length: %s' % len(page.text))

        tree = lxml.html.fromstring(page.text)
        d = {x.get('download'): x.get('href') for x in tree.cssselect('a.btn.server')}

        print('Writing to ' + self.filename)
        with open(self.filename, 'w') as f:
            yaml.dump(d, f, default_flow_style=False)
        print('Done downloading')

    def list_exists(self):
        return os.path.isfile(self.filename)

    def get_list(self):
        if not self.list_exists():
            self.update()
        with open(self.filename, 'r') as f:
            return yaml.safe_load(f)

    @requires_list
    def get_latest_jar(self):
        pass

    def requires_list(func):
        @wraps(func)
        def func_wrapper(self, *args, **kwargs):
            if not self.list_exists():
                self.update()
            return func(*args, **kwargs)
        return func_wrapper


if __name__ == '__main__':
    JarList().get_latest_jar()
