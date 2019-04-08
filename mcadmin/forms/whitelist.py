from flask_wtf import FlaskForm
from wtforms import StringField, validators

OPERATION_ADD = 'add',
OPERATION_REMOVE = 'remove'


class WhitelistForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[
            validators.DataRequired('Please specify a name.')
        ]
    )
