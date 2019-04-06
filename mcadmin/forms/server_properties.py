from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms.widgets import TextArea


class ServerPropertiesForm(FlaskForm):
    properties = StringField(
        'Properties',
        validators=[
            validators.Length(0, 10_000, 'Length of properties file cannot exceed 10,000 characters.')
        ],
        widget=TextArea())
