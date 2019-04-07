from flask_wtf import FlaskForm
from wtforms import StringField, validators

OPERATION_ADD = 'add',
OPERATION_REMOVE = 'remove'


class WhitelistOperationForm(FlaskForm):
    operation = StringField(
        'Operation',
        validators=[
            validators.DataRequired('Operation is missing'),
            validators.AnyOf('add', 'remove')
        ])

    name = StringField(
        'Name',
        validators=[
            validators.DataRequired('Please specify a name')
        ]
    )
