# mcadmin/server.py
import logging
import os.path

from flask import Flask
from flask_login import LoginManager
from flask_scss import Scss

# configure Flask
from mcadmin.model.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

login_manager = LoginManager(app)
Scss(app)

# register routes
# noinspection PyUnresolvedReferences
from mcadmin.routes import index, register, login, console_panel, logout

login_manager.login_view = '/login'
login_manager.login_message = 'Please log in'


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
