# mcadmin/io/registration.py

import os.path

AUTH_FILE = 'credentials.bfe'


def is_registered():
    return os.path.isfile(AUTH_FILE)


def save_password(password):
    with open(AUTH_FILE, 'w') as f:
        f.write(password)
