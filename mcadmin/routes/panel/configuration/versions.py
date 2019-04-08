from flask import render_template
from flask_login import login_required

from mcadmin.main import app


@app.route('/panel/configuration/versions')
@login_required
def server_versions():
    return render_template('panel/config/server_versions.html')
