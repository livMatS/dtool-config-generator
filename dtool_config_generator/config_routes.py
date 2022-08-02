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
