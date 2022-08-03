from flask import render_template, abort

from flask_smorest import Blueprint


bp = Blueprint("main", __name__, template_folder='templates')


@bp.route('/')
def index():
    """Show index page."""
    return render_template('index.html')

