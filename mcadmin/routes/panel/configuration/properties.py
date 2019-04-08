from flask import flash, redirect, url_for, render_template
from flask_login import login_required

from mcadmin.forms.server_properties import ServerPropertiesForm
from mcadmin.io.files.server_properties import SERVER_PROPERTIES
from mcadmin.main import app


@app.route('/panel/configuration/properties', methods=['GET', 'POST'])
@login_required
def edit_server_properties():
    """
    Presents the user with an interface for editing the server.properties file, as well as access to the other
    configuration screens.
    """
    form = ServerPropertiesForm()

    if form.validate_on_submit():
        SERVER_PROPERTIES.write(form.properties.data)
        flash('Server properties updated.')
        return redirect(url_for('edit_server_properties'))

    form.properties.data = SERVER_PROPERTIES.reads()
    return render_template('panel/config/properties.html', form=form)
