from flask import render_template, abort

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
from flask_smorest import Blueprint

from jinja2 import TemplateNotFound

bp = Blueprint("main", __name__, template_folder='templates')


@bp.route('/', defaults={'page': 'index'})
@bp.route('/<page>')
def show(page):
    """Show page."""
    try:
        return render_template(f'{page}.html')
    except TemplateNotFound:
        abort(404)


