from flask import request, abort, render_template, redirect

from mcadmin.forms.registration import RegistrationForm
from mcadmin.io.registration import is_registered, save_password
from mcadmin.main import app


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    This is the page for registering an administrative password for the MCAdmin instance.

    If an administrative password has already been registered, then a HTTP 401 Unauthorized response will be sent.

    If the registration form is submitted, the entered password will be validated and then saved to disk. The user will
    then be redirected to the index page.
    """
    if is_registered():
        abort(401, 'This server is already registered')

    form = RegistrationForm()

    if form.validate_on_submit():
        password = request.form['password']
        save_password(password)
        return redirect('/')
    else:
        return render_template('registration.html', form=form)
