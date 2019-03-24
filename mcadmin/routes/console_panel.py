# mcadmin/routes/console_panel.py
import logging

from flask import render_template, Response, request, abort
from flask_login import login_required

from mcadmin.util import require_json
from mcadmin.main import app
from mcadmin.server import server
from mcadmin.server.server import is_server_running, CONSOLE_OUTPUT_COND, console_output, ServerNotRunningError

LOGGER = logging.getLogger(__name__)
SERVER_NOT_RUNNING_ERR_CODE = 'mcadmin:err:server_not_running'
MAX_INPUT_LENGTH = 255


@app.route('/panel/console', methods=['GET', 'POST'])
@login_required
def console_panel():
    """
    Route for displaying the server console control panel and entering console commands.

    GET:
        Will simply render the console_panel.html template.
        Template arguments:
            `console_history`: The console output buffer that should be displayed to the user so they can see what went
            on the console while they were not looking.

    POST:
        Receives a JSON object with the following schema:
            "input_line": <str>  <- Console line to enter

        The "input_line" value will be passed into the Minecraft Server Console.

        A HTTP 409 Conflict response will be returned if the server is not running.

        A HTTP 400 Bad Request error will be raised if:
            - "input_line" key is not present or has no value
            - "input_line" is over MAX_INPUT_LENGTH characters long
    """
    if request.method == 'GET':
        return render_template('console_panel.html', console_history=''.join(console_output))
    else:
        assert request.method == 'POST'
        require_json()

        data = request.get_json()
        assert data is not None

        input_line = data.get('input_line')
        if input_line is None:
            abort(400, 'No `input_line')
        elif len(input_line) > MAX_INPUT_LENGTH:
            abort(400, 'Input line must not exceed %d characters.' % MAX_INPUT_LENGTH)

        try:
            server.input_line(input_line)
        except ServerNotRunningError:
            return 'Server is not running', 409

        return '', 204


@app.route('/panel/console/stream')
@login_required
def console_panel_stream():
    """
    Returns a Response (type: text/event-stream) to be consumed by an EventSource.

    The Minecraft Server console's messages will be streamed.
    If the server is not running, SERVER_NOT_RUNNING_ERR_CODE will be streamed instead every 10 seconds.

    """

    def generator():
        try:
            is_first_iter = True
            while True:
                with CONSOLE_OUTPUT_COND:
                    if is_server_running():
                        # Do not attempt to send any data in first loop iteration.
                        # This is because there is usually no data to send.
                        if not is_first_iter:
                            yield 'data: ' + str(console_output[-1]) + '\n\n'
                        CONSOLE_OUTPUT_COND.wait()
                    else:
                        yield 'data: ' + SERVER_NOT_RUNNING_ERR_CODE + '\n\n'
                        CONSOLE_OUTPUT_COND.wait()
                is_first_iter = False
        except GeneratorExit as e:
            # This means the user quit the console page
            LOGGER.debug('GeneratorExit console_panel_stream: ' + str(e))

    return Response(generator(), mimetype='text/event-stream')
