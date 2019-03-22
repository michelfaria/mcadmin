# mcadmin/routes/status_panel.py
import json

from flask import render_template, request, abort, Response
from flask_login import login_required
from mcadmin.server import server

from mcadmin.main import app
from mcadmin.server.server import ServerAlreadyRunningError, ServerNotRunningError


@app.route('/status', methods=['GET', 'POST'])
@login_required
def status_panel():
    if request.method == 'GET':
        return render_template('status_panel.html')
    else:
        assert request.method == 'POST'

        data = request.get_json()
        if data is None or data.get('action') is None:
            return abort(Response('No action', 400))

        action = data['action']

        if action == 'turn_on':
            jvm_args = data.get('jvm_args', '')
            return turn_on(jvm_args)
        elif action == 'turn_off':
            return turn_off()
        else:
            return abort(Response('Unknown action', 400))


def turn_on(jvm_args):
    try:
        server.start(jvm_params=jvm_args)
    except ServerAlreadyRunningError:
        return abort(Response('Server is already running', 409))


def turn_off():
    try:
        server.stop()
    except ServerNotRunningError:
        return abort(Response('Server is not running'), 409)
