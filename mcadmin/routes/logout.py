# mcadmin/routes/logout.py
from flask_login import login_required, logout_user
from werkzeug.utils import redirect

from flask import session, flash, get_flashed_messages

from mcadmin.main import app


@app.route('/logout')
@login_required
def logout():
    logout_user()

    # clear flashed messages
    # for some reason, flashed messages were persisting
    get_flashed_messages()

    return redirect('/')
