from flask import render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_smorest import Blueprint

# from .schemas import TestResponseSchema

bp = Blueprint("generate", __name__, template_folder='templates', url_prefix="/generate")


def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@bp.route("/config", methods=["GET"])
@login_required
def config():
    """Generate dtool config for user."""
    user = {
        'id': current_user.username,
        'name': "Test User",
        'email': "test@mail.com"
    }
    #content = render_template('dtool.json', user=user)
    return  current_app.response_class(
        stream_template('dtool.json', user=user),
        mimetype='application/json',
        headers={"Content-Disposition":
                     "attachment;filename=dtool.json"}
    )