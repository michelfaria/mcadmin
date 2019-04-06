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
    return redirect('/')
