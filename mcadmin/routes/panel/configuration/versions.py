from flask import render_template, request, redirect, url_for
from flask_login import login_required

from mcadmin.config import CONFIG, USE_SERVER_JAR, SECTION_MAIN
from mcadmin.forms.config.version_form import SetVersionForm
from mcadmin.io.files.server_list import SERVER_LIST
from mcadmin.main import app


@app.route('/panel/configuration/versions')
@login_required
def server_versions():
    version_form = SetVersionForm()
    versions = SERVER_LIST.versions()
    current_jar = CONFIG[SECTION_MAIN][USE_SERVER_JAR]

    if version_form.is_submitted() and version_form.validate():
        # TODO: stuff here
        pass

    return render_template('panel/config/server_versions.html',
                           current_jar=current_jar,
                           version_form=version_form,
                           versions=versions)
