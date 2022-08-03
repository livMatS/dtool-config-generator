#
# Copyright 2022 Johannes Laurin Hörmann
#
# ### MIT license
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""Routes for generating dtool config and readme template files."""
import os.path
import logging

from flask import current_app, flash, render_template, stream_with_context
from flask_login import login_required, current_user
from flask_smorest import Blueprint

from jinja2 import Environment, FileSystemLoader

from dtool_config_generator.forms import ConfirmationForm
from dtool_config_generator.utils import confirmation_required


logger = logging.getLogger(__name__)


bp = Blueprint("generate", __name__, template_folder='templates', url_prefix="/generate")


@stream_with_context
def stream_config_template(**context):
    if 'DTOOL_CONFIG_TEMPLATE' in current_app.config:
        dtool_config_template = current_app.config['DTOOL_CONFIG_TEMPLATE']
        logger.debug("Use DTOOL_CONFIG_TEMPLATE=%s", dtool_config_template)
        template_dir = os.path.dirname(dtool_config_template)
        template_name = os.path.basename(dtool_config_template)

        env = Environment(loader=FileSystemLoader(template_dir))
        t = env.get_template(template_name)
    else:
        logger.debug("Use default template directory")
        current_app.update_template_context(context)
        t = current_app.jinja_env.get_template('dtool.json')

    logger.debug("Render with context %s", context)
    rv = t.stream(**context)
    rv.enable_buffering(5)
    return rv


@stream_with_context
def stream_readme_template(**context):
    if 'DTOOL_README_TEMPLATE' in current_app.config:
        template_dir = os.path.dirname(current_app.config['DTOOL_README_TEMPLATE'])
        template_name = os.path.basename(current_app.config['DTOOL_README_TEMPLATE'])

        env = Environment(loader=FileSystemLoader(template_dir))
        t = env.get_template(template_name)
    else:
        current_app.update_template_context(**context)
        t = current_app.jinja_env.get_template('dtool_readme.yml')

    rv = t.stream(**context)
    rv.enable_buffering(5)
    return rv


def generate_config():
    """Streams back filled-out config template."""
    logger.debug("Generate config for %s", current_user.username)
    extended_context = current_app.template_context_builder.run()
    return current_app.response_class(
        stream_config_template(user=current_user, **extended_context),
        mimetype='application/json',
        headers={"Content-Disposition":
                     "attachment;filename=dtool.json"}
    )


@bp.route("/config", methods=["GET", "POST"])
@login_required
@confirmation_required
def config():
    """Generate dtool config for user."""
    form = ConfirmationForm()

    if form.validate_on_submit():
        return generate_config()

    flash("""
        The generated dool.json config file will contain
        storage infrastructure access
        credentials. Don't lose it, keep it safe.
        Regenerating a config file will invalidate all
        previously issued access credentials.""")
    return render_template('generate/confirm.html', form=form)


@bp.route("/readme", methods=["GET"])
@login_required
@confirmation_required
def readme():
    """Generate dtool readme template for user."""
    return current_app.response_class(
        stream_readme_template(user=current_user),
        mimetype='application/yaml',
        headers={"Content-Disposition":
                     "attachment;filename=dtool_readme.yml"}
    )