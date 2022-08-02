import os.path

from flask import render_template, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_smorest import Blueprint

from jinja2 import Environment, FileSystemLoader

from .utils import confirmation_required

bp = Blueprint("generate", __name__, template_folder='templates', url_prefix="/generate")


def stream_config_template(**context):
    if 'DTOOL_CONFIG_TEMPLATE' in current_app.config:
        template_dir = os.path.dirname(current_app.config['DTOOL_CONFIG_TEMPLATE'])
        template_name = os.path.basename(current_app.config['DTOOL_CONFIG_TEMPLATE'])

        env = Environment(loader=FileSystemLoader(template_dir))
        t = env.get_template(template_name)
    else:
        current_app.update_template_context(context)
        t = current_app.jinja_env.get_template('dtool.json')

    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@bp.route("/config", methods=["GET"])
@login_required
@confirmation_required
def config():
    """Generate dtool config for user."""
    user = {
        'id': current_user.username,
        'name': "Test User",
        'email': "test@mail.com"
    }
    #content = render_template('dtool.json', user=user)
    return current_app.response_class(
        stream_config_template(user=user),
        mimetype='application/json',
        headers={"Content-Disposition":
                     "attachment;filename=dtool.json"}
    )