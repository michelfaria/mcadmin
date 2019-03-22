# mcadmin/routes/console_panel.py
import logging

from flask import render_template, Response
from flask_login import login_required

from mcadmin.main import app
from mcadmin.server.server import is_server_running, CONSOLE_OUTPUT_COND, console_output

LOGGER = logging.getLogger(__name__)
SERVER_NOT_RUNNING_ERR_CODE = 'mcadmin:err:server_not_running'


@app.route('/console_panel')
@login_required
def console_panel():
    return render_template('console_panel.html')


@app.route('/console_panel_stream')
@login_required
def console_panel_stream():
    """
    Returns a Response (type: text/event-stream) to be consumed by an EventSource.

    The Minecraft Server console's messages will be streamed.
    If the server is not running, SERVER_NOT_RUNNING_ERR_CODE will be streamed instead every 10 seconds.

    """
    def generator():
        try:
            while True:
                with CONSOLE_OUTPUT_COND:
                    if is_server_running():
                        CONSOLE_OUTPUT_COND.wait()
                        yield 'data: ' + str(console_output[-1]) + '\n\n'
                    else:
                        yield 'data: ' + SERVER_NOT_RUNNING_ERR_CODE + '\n\n'
                        # Wait a little before checking again
                        CONSOLE_OUTPUT_COND.wait(timeout=10)
        except GeneratorExit as e:
            # This means the user quit the console page
            LOGGER.debug('GeneratorExit console_panel_stream: ' + str(e))

    return Response(generator(), mimetype='text/event-stream')
