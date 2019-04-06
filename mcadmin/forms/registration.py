from flask_wtf import FlaskForm
from wtforms import PasswordField, validators


class RegistrationForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[
            validators.DataRequired('Please enter a password!'),
            validators.Length(8, 1_000, 'Please enter a password that is between 8 and 1,000 characters long. This is'
                                        ' to ensure the safety of your server.')
        ],
        render_kw={
            'class': 'mc-input'
        })
    confirm_password = PasswordField(
        'Repeat Password',
        validators=[
            validators.DataRequired('Please repeat your password to ensure that you typed your password correctly.'),
            validators.EqualTo('password', 'The repeated password did not match the one you typed above. Please enter'
                                           ' your password again to make sure you entered your password correctly.')
        ],
        render_kw={
            'class': 'mc-input'
        }
    )
