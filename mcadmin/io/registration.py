import os.path

_AUTH_FILE = 'credentials.bfe'


def is_registered():
    """
    :returns: true if the MCAdmin instance is registered with an administrative password.
    """
    return os.path.isfile(_AUTH_FILE)


def save_password(password):
    """
    Writes the administrative password to disk.
    :param password: Administrative password to be saved.

    TODO: Password hashing algorithm.
    """
    with open(_AUTH_FILE, 'w+') as f:
        f.write(password)


def _get_hashed_password():
    with open(_AUTH_FILE, 'r') as f:
        return f.read()


def password_matches(password):
    """
    :param password: Password to compare to
    :return: Returns true if the password matches the one used for the administrative account.
    """
    return password == _get_hashed_password()
