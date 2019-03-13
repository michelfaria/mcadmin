# mcadmin/forms/login_form.py

from flask_wtf import FlaskForm
from wtforms import PasswordField, validators


class LoginForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[
            validators.DataRequired('Please enter the administrative password.')
        ],
        render_kw={
            'class': 'mc-input'
        })
