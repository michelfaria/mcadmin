# mcadmin/server.py

import os.path

from flask import Flask
from flask_scss import Scss

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
Scss(app)

# noinspection PyUnresolvedReferences
from mcadmin.routes import index, register


def start():
    app.run()
