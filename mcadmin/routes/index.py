import logging

from flask import redirect, url_for

from mcadmin.io.registration import is_registered
from mcadmin.main import app

LOGGER = logging.getLogger(__name__)


@app.route('/')
def index():
    """
    This is the landing page of the website.

    The end-user should be redirected to the registration page if a password has not been registered for this instance
    of MCAdmin. If the MCAdmin instance is registered, however, the user will be redirected to the Status Panel page.

    Naturally, the status panel requires authentication, so the user should be redirected to the login page if they are
    not yet logged in.
    """
    if not is_registered():
        return redirect(url_for('register'))
    return redirect(url_for('status_panel'))
