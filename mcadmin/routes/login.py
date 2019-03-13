# mcadmin/routes/login.py

from flask import render_template, flash, redirect, request
from flask_login import login_user

from mcadmin.forms.login_form import LoginForm
from mcadmin.io.registration import password_matches
from mcadmin.model.user import User
from mcadmin.server import app


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    user = User(1)

    if form.validate_on_submit():
        input_password = request.form['password']
        if not password_matches(input_password):
            flash('Incorrect password')
        elif not login_user(user, remember=True):
            flash('Unable to log you in')
        else:
            flash('Logged in')
            return redirect('/')

    return render_template('login.html', form=form)
