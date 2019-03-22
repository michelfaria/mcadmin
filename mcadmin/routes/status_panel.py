# mcadmin/routes/status_panel.py
import json
import logging
import threading

from flask import render_template, request, abort, Response
from flask_login import login_required

from mcadmin.decorators import json_route
from mcadmin.server import server

from mcadmin.main import app
from mcadmin.server.server import ServerAlreadyRunningError, ServerNotRunningError, is_server_running, \
    SERVER_STATUS_CHANGE

LOGGER = logging.getLogger(__name__)


@app.route('/status_panel', methods=['GET', 'POST'])
@login_required
@json_route
def status_panel():
    """
    The status panel displays the most important information about the server, such as Online Status, Uptime,
    Peak Activity, etc.

    GET:
        Will simply render the status panel.

    POST:
        Will take a JSON object of the following schema:
            "action": <str>,           <- {"turn_on" | "turn_off"}
            "jvm_args": <str | None>,  <- JVM Arguments (Optional)

        A HTTP 400 Bad Request response will be sent if:
            - The request body is not valid JSON
            - There is no "action" key in the JSON object

        The "action" key describes what action should be performed by the status panel.

        Actions:
            "turn_on": Start the server. If the server is already started, it will respond with a HTTP 409 Conflict.
            "turn_off": Stop the server. If the server is not running, it will respond with a HTTP 409 Conflict.

        Optional Keys:
            "jvm_args": Used in conjunction with the "turn_on" action. These JVM arguments will be passed to the server
            startup command. FIXME: It may be possible to perform shell command injection by adding semicolons to
            this field.


    """
    if request.method == 'GET':
        return render_template('status_panel.html')
    else:
        assert request.method == 'POST'

        data = request.get_json()
        assert data is not None

        action = data.get('action')
        if action is None:
            abort(400, 'No action')

        if action == 'turn_on':
            jvm_args = data.get('jvm_args', '')
            return turn_on(jvm_args)
        elif action == 'turn_off':
            return turn_off()
        else:
            abort(400, 'Unknown action')


@app.route('/status_panel_stream')
@login_required
def status_panel_stream():
    """
    Streams a JSON object with the following format every time the server status changes:
    {
        "is_server_running": <boolean>,  <- True if the server is running; false otherwise
        "uptime": <int>,                 <- Running time of the server in milliseconds
        "peak_activity": <int>           <- Highest amounts of simultaneous players connected
    }
    """

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
    """
    Turns the server on.
    Returns a HTTP 409 Conflict response if the server is already running.

    :param jvm_args: Arguments used in the initialization of the JVM.
    :return: flask.Response
    """
    try:
        server.start(jvm_params=jvm_args)
        return Response(status=200)
    except ServerAlreadyRunningError:
        abort(409, 'Server is already running')


def turn_off():
    """
    Turns the server off.
    Returns a HTTP 409 Conflict response if the server is not running.

    :return: flask.Response
    """
    try:
        server.stop()
        return Response(status=200)
    except ServerNotRunningError:
        abort(409, 'Server is not running')
