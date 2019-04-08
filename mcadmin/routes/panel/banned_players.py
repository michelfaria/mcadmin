from flask import render_template, flash, redirect, url_for
from flask_login import login_required

from mcadmin.exception import PublicError
from mcadmin.forms.banned_players import BanPlayerForm, PardonPlayerForm
from mcadmin.io.files.banned_players import BANNED_PLAYERS
from mcadmin.main import app


@app.route('/panel/banned_players')
@login_required
def banned_players_panel():
    ban_form = BanPlayerForm()
    pardon_form = PardonPlayerForm()

    ban_list = BANNED_PLAYERS.reads()

    return render_template('panel/banned_players.html', ban_form=ban_form, pardon_form=pardon_form, ban_list=ban_list)


@app.route('/panel/banned_players/ban', methods=['POST'])
@login_required
def ban_player():
    ban_form = BanPlayerForm()

    if ban_form.validate_on_submit():
        name = ban_form.name.data
        reason = ban_form.reason.data
        try:
            BANNED_PLAYERS.ban(name, reason)
            flash('User %s banned.' % name)
        except PublicError as e:
            flash('Error: ' + str(e))

    return redirect(url_for('banned_players_panel'))


@app.route('/panel/banned_players/pardon', methods=['POST'])
@login_required
def pardon_player():
    pardon_form = PardonPlayerForm()

    if pardon_form.validate_on_submit():
        name = pardon_form.name.data
        try:
            BANNED_PLAYERS.pardon(name)
            flash('User %s pardoned.' % name)
        except PublicError as e:
            flash('Error: ' + str(e))

    return redirect(url_for('banned_players_panel'))
