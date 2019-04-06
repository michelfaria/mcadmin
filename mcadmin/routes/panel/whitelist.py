from flask import render_template, abort, Response
from flask_login import login_required

from mcadmin.io.mc_profile import ProfileAPIError
from mcadmin.main import app
from mcadmin.io import mc_profile
from mcadmin.io.files import WHITELIST_FILE, EntryNotFound


@app.route('/panel/whitelist')
@login_required
def whitelist_panel():
    return render_template('panel/whitelist.html')


@app.route('/panel/whitelist/add/<username>')
@login_required
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


@app.route('/panel/whitelist/remove/<username>')
@login_required
def whitelist_remove(username):
    try:
        WHITELIST_FILE.remove(username)
    except EntryNotFound:
        abort(404, 'User %s was not found in the whitelist' % username)

    return '', 204
