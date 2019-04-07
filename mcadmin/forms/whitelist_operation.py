from flask_wtf import FlaskForm
from wtforms import StringField, validators, SelectField

OPERATION_ADD = 'add',
OPERATION_REMOVE = 'remove'


class WhitelistOperationForm(FlaskForm):
    operation = SelectField(
        'Operation',
        choices=[
            ('Add', OPERATION_ADD),
            ('Remove', OPERATION_REMOVE)
        ],
        validators=[
            validators.DataRequired('Please enter an operation.')
        ]
    )

    name = StringField(
        'Name',
        validators=[
            validators.DataRequired('Please specify a name.')
        ]
    )
