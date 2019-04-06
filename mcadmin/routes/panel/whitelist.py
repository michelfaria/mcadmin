from flask import render_template

from mcadmin.main import app


@app.route('/panel/whitelist')
def whitelist_panel():
    return render_template('panel/whitelist.html')
