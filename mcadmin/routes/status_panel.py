# mcadmin/routes/status_panel.py
import json
import logging
import threading

from flask import render_template, request, abort, Response
from flask_login import login_required
from mcadmin.server import server

from mcadmin.main import app
from mcadmin.server.server import ServerAlreadyRunningError, ServerNotRunningError, is_server_running, SERVER_STATUS_CHANGE

LOGGER = logging.getLogger(__name__)


@app.route('/status_panel', methods=['GET', 'POST'])
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
                with SERVER_STATUS_CHANGE:
                    SERVER_STATUS_CHANGE.wait(timeout=60)
        except GeneratorExit as e:
            LOGGER.debug('GeneratorExit status_panel_stream: ' + str(e))

    return Response(generator(), mimetype='text/event-stream')


def turn_on(jvm_args):
    try:
        server.start(jvm_params=jvm_args)
        return Response(status=200)
    except ServerAlreadyRunningError:
        return abort(Response('Server is already running', 409))


def turn_off():
    try:
        server.stop()
        return Response(status=200)
    except ServerNotRunningError:
        return abort(Response('Server is not running', 409))
