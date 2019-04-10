from flask_wtf import FlaskForm
from wtforms import validators, StringField


class SetVersionForm(FlaskForm):
    jar_name = StringField(
        validators=[
            validators.DataRequired('Please enter a jar name')
        ]
    )
