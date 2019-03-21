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
    if is_registered():
        if current_user.is_authenticated:
            return render_template('status_panel.html')
        else:
            return login_manager.unauthorized()
    else:
        return redirect(url_for('register'))


@app.route('/status_panel_stream')
@login_required
def status_panel_stream():
    def generator():
        try:
            while True:
                msg = {
                    'is_server_running': is_server_running(),
                    'uptime': 0,
                    'peak_activity': 0
                }
                yield 'data: ' + json.dumps(msg) + '\n\n'
                time.sleep(10)
        except GeneratorExit as e:
            LOGGER.debug('GeneratorExit status_panel_stream: ' + str(e))

    return Response(generator(), mimetype='text/event-stream')
