# mcadmin/io/registration.py

import os.path

AUTH_FILE = 'credentials.bfe'


def is_registered():
    """
    :returns: true if the MCAdmin instance is registered with an administrative password.
    """
    return os.path.isfile(AUTH_FILE)


def save_password(password):
    """
    Writes the administrative password to disk.
    :param password: Administrative password to be saved.

    TODO: Password hashing algorithm.
    """
    with open(AUTH_FILE, 'w+') as f:
        f.write(password)


def _get_hashed_password():
    with open(AUTH_FILE, 'r') as f:
        return f.read()


def password_matches(password):
    """
    :param password: Password to compare to
    :return: Returns true if the password matches the one used for the administrative account.
    """
    return password == _get_hashed_password()
