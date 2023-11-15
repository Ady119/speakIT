from flask import render_template, Blueprint

error = Blueprint('error', __name__)

def forbidden(e):
    # No redirects here, just render the 403 page directly
    return render_template('403.html'), 403