from flask import render_template, abort

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

from jinja2 import TemplateNotFound

bp = Blueprint("main", __name__, template_folder='templates')


@bp.route('/')
def index():
    """Show index page."""
    return render_template('index.html')

