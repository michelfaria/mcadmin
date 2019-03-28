# mcadmin/routes/configuration_panel.py
from flask import render_template, flash, url_for, redirect

from mcadmin.forms.server_properties_form import ServerPropertiesForm
from mcadmin.io import server_properties
from mcadmin.main import app

MAX_PROPERTIES_INPUT_LEN = 2000


@app.route('/panel/configuration', methods=['GET', 'POST'])
def configuration_panel():
    form = ServerPropertiesForm()

    if form.validate_on_submit():
        server_properties.write(form.properties)
        flash('Server properties updated.')
        return redirect(url_for('configuration_panel'))
    else:
        exists = server_properties.exists()
        form.properties.data = server_properties.read() if exists else ''
        return render_template('configuration_panel.html', form=form, exists=exists)
