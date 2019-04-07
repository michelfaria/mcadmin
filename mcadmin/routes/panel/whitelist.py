from flask import render_template, flash, redirect, url_for
from flask_login import login_required

from mcadmin.exception import PublicError
from mcadmin.forms.whitelist_operation import WhitelistForm, OPERATION_ADD, OPERATION_REMOVE
from mcadmin.io import mc_profile
from mcadmin.io.whitelist import whitelist_io
from mcadmin.main import app


@app.route('/panel/whitelist', methods=['GET', 'POST'])
@login_required
def whitelist_panel():
    form = WhitelistForm()
    users = whitelist_io.read()
    return render_template('panel/whitelist.html', form=form, users=users)


@app.route('/panel/whitelist/add', methods=['POST'])
@login_required
def whitelist_add():
    form = WhitelistForm()

    if form.validate_on_submit():
        name = form.name.data
        try:
            uuid = mc_profile.uuid(name)
            whitelist_io.add(name, uuid)
            flash('%s added to whitelist' % name)
        except PublicError as e:
            flash('Error: ' + str(e))

    return redirect(url_for('whitelist_panel'))


@app.route('/panel/whitelist/remove', methods=['POST'])
@login_required
def whitelist_remove():
    form = WhitelistForm()

    if form.validate_on_submit():
        name = form.name.data
        try:
            whitelist_io.remove(name)
            flash('%s removed from whitelist' % name)
        except PublicError as e:
            flash('Error: ' + str(e))

    return redirect(url_for('whitelist_panel'))
