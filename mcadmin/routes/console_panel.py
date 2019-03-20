# mcadmin/routes/console_panel.py
from flask import render_template, Response
from flask_login import login_required
from mcadmin.server.server import proc, is_server_running

from mcadmin.main import app


@app.route('/console_panel')
@login_required
def console_panel():
    return render_template('console_panel.html')


@app.route('/console_panel_stream')
@login_required
def stream():
    return Response(console_stream(), mimetype='text/event-stream')


def console_stream():
    while is_server_running():
        assert proc is not None and proc.poll() is None
        out = proc.stdout.readlines()
        if len(out) > 0:
            yield out
    return 'Server stream closed'
