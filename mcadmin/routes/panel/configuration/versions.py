from flask import render_template, flash
from flask_login import login_required

from mcadmin.config import CONFIG, USE_SERVER_JAR, SECTION_MAIN
from mcadmin.forms.config.version_form import SetVersionForm
from mcadmin.io.files.server_list import SERVER_LIST
from mcadmin.io.server.server import SERVER
from mcadmin.main import app


@app.route('/panel/configuration/versions', methods=['GET', 'POST'])
@login_required
def server_versions():
    version_form = SetVersionForm()
    versions = SERVER_LIST.versions()

    if version_form.is_submitted() and version_form.validate():
        # Update configuration with the new jar name
        CONFIG[SECTION_MAIN][USE_SERVER_JAR] = version_form.jar_name.data
        flash('Server executable set to be %s. It will be used next time the server boots.' % SERVER.jar)

    return render_template('panel/config/server_versions.html',
                           current_jar=SERVER.jar,
                           version_form=version_form,
                           versions=versions)
