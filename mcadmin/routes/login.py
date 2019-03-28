# mcadmin/routes/login.py

from flask import render_template, flash, redirect, request, url_for
from flask_login import login_user

from mcadmin.forms.login_form import LoginForm
from mcadmin.io.registration import password_matches, is_registered
from mcadmin.main import app
from mcadmin.model.user import User


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Viewing the login page first requires the MCAdmin instance to be registered with an administrative password. If
    there is not one registered, then the user will be redirected to the registration page.

    If the login form is submitted, this method will check if the password entered matches the one stored in disk. If
    the check passes, the user will be redirected to the index page. If the check fails, the user will receive an error
    message.

    In the rare event that the passwords match but Flask fails to log in, the user will also receive an error message.
    I don't think that will ever happen, however.
    """
    if not is_registered():
        return redirect(url_for('register'))

    form = LoginForm()

    # Since there is only one user per MCAdmin instance, the User id will always be 1
    user = User(1)

    if form.validate_on_submit():
        input_password = request.form['password']
        if not password_matches(input_password):
            flash('Incorrect password')
        elif not login_user(user, remember=True):
            flash('Unable to log you in')
        else:
            return redirect('/')

    return render_template('login.html', form=form)
