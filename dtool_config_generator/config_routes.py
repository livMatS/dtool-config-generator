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
import json

from flask import current_app, jsonify
from flask_login import login_required
from flask_smorest import Blueprint

import dtool_config_generator

from .utils import admin_required

bp = Blueprint("config", __name__, url_prefix="/config")


def serializable(obj):
    try:
        json.dumps(obj)
    except:
        return str(obj)
    else:
        return obj


def to_dict(obj):
    """Convert configuration into dict."""
    exclusions = [
        "JWT_PRIVATE_KEY",
    ]  # config keys to exclude
    d = {"version": dtool_config_generator.__version__}
    for k, v in obj.items():
        # select only capitalized fields
        if k.upper() == k and k not in exclusions:
            d[k.lower()] = serializable(v)
    print(d)
    return d


@bp.route("/info", methods=["GET"])
@login_required
@admin_required
def server_config():
    """Return the JSON-serialized server configuration."""
    # return Config.to_dict()

    return jsonify(to_dict(current_app.config))
