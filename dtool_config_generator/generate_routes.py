from flask import abort
from flask_smorest import Blueprint

from dtool_config_generator import AuthenticationError
import dtool_config_generator.utils

from .schemas import TestResponseSchema

bp = Blueprint("config", __name__, url_prefix="/config")


@bp.route("/generate/<username>", methods=["GET"])
@bp.response(200, TestResponseSchema)
@jwt_required()
def generate(username):
    """Generate dtool config for user."""
    token_username = get_jwt_identity()

    # return dtool_lookup_server.utils.get_user_info(username)
    return token_username