from flask import render_template
from flask_login import login_required

from mcadmin.main import app


@app.route('/panel/banned_players')
@login_required
def banned_players_panel():
    return render_template('panel/banned_players.html')
