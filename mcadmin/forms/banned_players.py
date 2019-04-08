from flask_wtf import FlaskForm
from wtforms import StringField, validators


class BanPlayerForm(FlaskForm):
    name = StringField(
        'Username',
        validators=[
            validators.DataRequired('Please enter what player is to be banned.')
        ])
    reason = StringField(
        'Ban Reason',
        validators=[
            validators.Length(-1, 300, 'Please limit the ban reason to 300 characters.')
        ])


class PardonPlayerForm(FlaskForm):
    name = StringField(
        validators=[
            validators.DataRequired('Please specify whom to pardon.')
        ])
