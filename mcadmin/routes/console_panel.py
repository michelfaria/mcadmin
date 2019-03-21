# mcadmin/routes/console_panel.py
import logging
import time

from flask import render_template, Response
from flask_login import login_required

from mcadmin.main import app
from mcadmin.server.server import proc, is_server_running

LOGGER = logging.getLogger(__name__)
SERVER_NOT_RUNNING_ERR_CODE = 'mcadmin:err:server_not_running'


@app.route('/console_panel')
@login_required
def console_panel():
    return render_template('console_panel.html')


@app.route('/console_panel_stream')
@login_required
def stream():
    return Response(console_stream(), mimetype='text/event-stream')


def console_stream():
    try:
        while True:
            if not is_server_running():
                yield 'data: ' + SERVER_NOT_RUNNING_ERR_CODE + '\n\n'
                time.sleep(10)  # Wait a little before checking again
                continue

            assert proc is not None and proc.poll() is None

            out = proc.stdout.readline()
            if len(out) > 0:
                yield 'data: ' + out + '\n\n'
            else:
                # Wait a little to prevent a lot of CPU usage
                time.sleep(1)
    except GeneratorExit as e:
        # Client quit console page
        LOGGER.debug('console_stream GeneratorExit: ' + str(e))
