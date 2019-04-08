from flask import url_for, redirect
from flask_login import login_required

from mcadmin.main import app


@app.route('/panel/configuration')
@login_required
def configuration_panel():
    """
    The configuration panel route.
    It simply redirects the user to the server properties editor as the landing page.
    """
    return redirect(url_for('edit_server_properties'))
