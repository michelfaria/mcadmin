import lxml.html
import requests
import yaml

LIST_FILENAME = 'server_list.yml'


def update_list():
    page = requests.get('https://mcversions.net/')
    print('Got Minecraft Servers list, length: %s' % len(page.text))

    tree = lxml.html.fromstring(page.text)
    d = {x.get('download'): x.get('href') for x in tree.cssselect('a.btn.server')}

    print('Writing to ' + LIST_FILENAME)
    with open(LIST_FILENAME, 'w') as f:
        yaml.dump(d, f, default_flow_style=False)

    print('Done')


if __name__ == '__main__':
    update_list()
