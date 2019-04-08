from flask import render_template, flash, url_for, redirect
from flask_login import login_required

from mcadmin.forms.server_properties import ServerPropertiesForm
from mcadmin.io.files.server_properties import server_properties_io
from mcadmin.main import app

MAX_PROPERTIES_INPUT_LEN = 2000


@app.route('/panel/configuration')
@login_required
def configuration_panel():
    return redirect(url_for('edit_server_properties'))


@app.route('/panel/edit/properties', methods=['GET', 'POST'])
@login_required
def edit_server_properties():
    form = ServerPropertiesForm()

    if form.validate_on_submit():
        server_properties_io.write(form.properties.data)
        flash('Server properties updated.')
        return redirect(url_for('edit_server_properties'))
    else:
        form.properties.data = server_properties_io.read() if server_properties_io.exists() else ''
        return render_template('panel/config/properties.html', form=form)
