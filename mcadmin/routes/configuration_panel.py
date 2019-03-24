# mcadmin/routes/configuration_panel.py
from flask import render_template

from mcadmin.main import app


@app.route('/panel/configuration')
def configuration_panel():
    return render_template('configuration_panel.html')
