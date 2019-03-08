# mcadmin/server.py

from flask import Flask, render_template, abort, request, redirect
import subprocess
import os.path

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

from mcadmin.routes import index, register

def start():
    app.run()
