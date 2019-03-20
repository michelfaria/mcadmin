# mcadmin/routes/index.py

from flask import render_template, redirect, url_for
from flask_login import current_user

from mcadmin.io.registration import is_registered
from mcadmin.main import app, login_manager


@app.route('/')
def index():
    if is_registered():
        if current_user.is_authenticated:
            return render_template('status_panel.html')
        else:
            return login_manager.unauthorized()
    else:
        return redirect(url_for('register'))
