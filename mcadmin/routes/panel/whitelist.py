from flask import render_template, abort
from flask_login import login_required

from mcadmin.io import mc_profile
from mcadmin.forms.whitelist_operation import WhitelistOperationForm, OPERATION_ADD, OPERATION_REMOVE
from mcadmin.io.files import WHITELIST_FILE, EntryNotFound
from mcadmin.io.mc_profile import ProfileAPIError
from mcadmin.main import app


@app.route('/panel/whitelist', methods=['GET', 'POST'])
@login_required
def whitelist_panel():
    form = WhitelistOperationForm()

    if form.validate_on_submit():
        if form.operation.data == OPERATION_ADD:
            return whitelist_add(form.name.data)
        else:
            assert form.operation.data == OPERATION_REMOVE
            return whitelist_remove(form.name.data)

    return render_template('panel/whitelist.html')


def whitelist_add(username):
    uuid = None
    try:
        uuid = mc_profile.uuid(username)
    except ProfileAPIError as e:
        abort(502, str(e))

    if uuid is None:
        abort(404, 'User %s not found' % username)

    WHITELIST_FILE.add(username, uuid)
    return '', 204


def whitelist_remove(username):
    try:
        WHITELIST_FILE.remove(username)
    except EntryNotFound:
        abort(404, 'User %s was not found in the whitelist' % username)

    return '', 204
