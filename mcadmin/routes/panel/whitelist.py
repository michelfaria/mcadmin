from flask import render_template, flash
from flask_login import login_required

from mcadmin.exception import PublicError
from mcadmin.forms.whitelist_operation import WhitelistOperationForm, OPERATION_ADD, OPERATION_REMOVE
from mcadmin.io import mc_profile
from mcadmin.io.whitelist import whitelist_io
from mcadmin.main import app


@app.route('/panel/whitelist', methods=['GET', 'POST'])
@login_required
def whitelist_panel():
    form = WhitelistOperationForm()

    if form.validate_on_submit():
        name = form.name.data

        try:
            if form.operation.data == OPERATION_ADD:
                whitelist_add(name)
                flash('%s added to whitelist' % name)
            elif form.operation.data == OPERATION_REMOVE:
                whitelist_remove(name)
                flash('%s removed from whitelist' % name)
            else:
                # Should never get here if validation works properly
                raise RuntimeError('Unknown operation')
        except PublicError as e:
            flash('Error: ' + str(e))

    return render_template('panel/whitelist.html')


def whitelist_add(username):
    """
    Add a user to the whitelist.

    :param str username: Name of the user to add to the whitelist
    :raises PublicError:
    """
    uuid = mc_profile.uuid(username)
    whitelist_io.add(username, uuid)


def whitelist_remove(username):
    """
    Remove a user from the whitelist.

    :param username: Name of the user to remove from the whitelist
    :raises PublicError:
    """
    whitelist_io.remove(username)
