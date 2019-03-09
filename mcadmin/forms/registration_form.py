# mcadmin/forms/registration_form.py

from flask_wtf import Form
from wtforms import PasswordField
from wtforms.validators import DataRequired


class RegistrationForm(Form):
    password = PasswordField('password', validators=[DataRequired()])
