# mcadmin/server.py

import os.path

from flask import Flask, redirect, url_for, request
from flask_login import LoginManager
from flask_scss import Scss

# configure Flask
from mcadmin.model.user import User

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

# set up login manager
login_manager = LoginManager()
login_manager.init_app(app)

# enable SCSS support
Scss(app)

# register routes
# noinspection PyUnresolvedReferences
from mcadmin.routes import index, register, login

login_manager.login_view = '/login'
login_manager.login_message = 'Please log in'


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def start():
    app.run()
