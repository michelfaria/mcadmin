# mcadmin/routes/logout.py
from flask import get_flashed_messages
from flask_login import login_required, logout_user
from werkzeug.utils import redirect

from mcadmin.main import app


@app.route('/logout')
@login_required
def logout():
    """
    Logs out the user and redirects them to the index page.
    """
    logout_user()

    # clear flashed messages
    # for some reason, flashed messages were persisting
    get_flashed_messages()

    return redirect('/')
