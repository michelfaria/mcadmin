# mcadmin/routes/index.py

from flask import render_template, redirect

from mcadmin.server import app
from mcadmin.io.registration import is_registered


@app.route('/')
def index():
    if is_registered():
        return render_template('index.html')
    else:
        return redirect('register')
