import logging
import re

import lxml.html
import requests

from mcadmin.io.files.files import YamlFileIO

_LOGGER = logging.getLogger(__name__)
_FILEPATH = 'server_list.yml'


class _ServerList(YamlFileIO):
    def __init__(self, *args, **kwargs):
        super().__init__(_FILEPATH, *args, **kwargs)

    def _update_if_not_exists(self):
        if not self.exists():
            self.update()

    def update(self):
        """
        Update the server list.

        Implementation notes:
            It gets an HTML page from mcversions.net that contains all links to all Minecraft Server versions.
            Then it parses that list to YAML and writes it to FILENAME.

            The format of the list is:

            {
                <version>: <link>
                ...
            }
        """
        _LOGGER.info('Updating Minecraft server executable link repository...')
        page = requests.get('https://mcversions.net/')
        _LOGGER.info('Got list, length: %s.' % len(page.text))

        tree = lxml.html.fromstring(page.text)
        d = {x.get('download'): x.get('href') for x in tree.cssselect('a.btn.server')}

        _LOGGER.debug('Writing to ' + _FILEPATH)
        self.write(d)
        _LOGGER.info('Server executable repository updated!')

    def load(self):
        """
        Returns the server list.
        """
        self._update_if_not_exists()
        return self.read()

    def versions(self):
        """
            :returns: A dictionary of all Minecraft versions, their full name and their respective server links in the
                      following format:
                {
                    "stable": [(version, full_name, link)],
                    "snapshot": [(version, full_name, link)]
                }

                The "stable" list is ordered by version number in descending order.
                The "snapshot" list is not ordered due to Mojang's weird snapshot versioning system.
            """
        stable = []
        snapshot = []

        for full_name, link in self.load().items():
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

    def latest_stable_version(self):
        """
        Returns the latest stable version of Minecraft.
        :return: (version, full_name, link)
        """
        return self.versions()['stable'][0]


SERVER_LIST = _ServerList()
