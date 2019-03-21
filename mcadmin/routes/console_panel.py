# mcadmin/routes/console_panel.py
import logging

from flask import render_template, Response
from flask_login import login_required

from mcadmin.main import app
from mcadmin.server.server import proc, is_server_running

LOGGER = logging.getLogger(__name__)


@app.route('/console_panel')
@login_required
def console_panel():
    return render_template('console_panel.html')


@app.route('/console_panel_stream')
@login_required
def stream():
    return Response(console_stream(), mimetype='text/event-stream')


def console_stream():
    while True:
        yield('Foo')
    # try:
    #     while True:
    #         if not is_server_running():
    #             yield 'Server is not running'
    #             continue
    #         assert proc is not None and proc.poll() is None
    #         out = proc.stdout.readlines()
    #         if len(out) > 0:
    #             yield out
    # except GeneratorExit as e:
    #     LOGGER.debug('console_stream GeneratorExit: ' + str(e))
