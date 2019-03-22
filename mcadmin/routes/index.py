# mcadmin/routes/index.py
import json
import logging
import time

from flask import render_template, redirect, url_for, Response
from flask_login import current_user, login_required

from mcadmin.io.registration import is_registered
from mcadmin.main import app, login_manager
from mcadmin.server.server import is_server_running

LOGGER = logging.getLogger(__name__)


@app.route('/')
def index():
    if not is_registered():
        return redirect(url_for('register'))
    elif not current_user.is_authenticated:
        return login_manager.unauthorized()
    else:
        return redirect(url_for('status_panel'))
