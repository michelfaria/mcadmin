from flask import render_template
from flask_login import login_required

from mcadmin.io.files.server_list import SERVER_LIST
from mcadmin.main import app


@app.route('/panel/configuration/versions')
@login_required
def server_versions():
    versions = SERVER_LIST.versions()
    return render_template('panel/config/server_versions.html', versions=versions)
