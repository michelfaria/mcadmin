# mcadmin/routes/register.py

from flask import request, abort, render_template, redirect
from mcadmin.server import app
from mcadmin.io.registration import is_registered, save_password
from mcadmin.forms.registration_form import RegistrationForm


@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_registered():
        return abort(401)
    form = RegistrationForm()
    if form.validate_on_submit():
        password = request.form['password']
        save_password(password)
        return redirect('/')
    return render_template('registration.html', form=form)
