from flask import render_template
from flask_login import login_required

from mcadmin.config import CONFIG, USE_SERVER_JAR, SECTION_MAIN
from mcadmin.io.files.server_list import SERVER_LIST
from mcadmin.main import app


@app.route('/panel/configuration/versions')
@login_required
def server_versions():
    versions = SERVER_LIST.versions()

    current_jar = CONFIG[SECTION_MAIN][USE_SERVER_JAR]
    assert current_jar is not None
    if current_jar is '':
        current_jar = 'There is no current jar.'

    return render_template('panel/config/server_versions.html', current_jar=current_jar, versions=versions)
