import sys

from flask import Flask, request
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_smorest import (
    Api,
    Blueprint
)
from flask_jwt_extended import JWTManager


class ValidationError(ValueError):
    pass


class AuthenticationError(ValueError):
    pass


class AuthorizationError(ValueError):
    pass


class UnknownBaseURIError(KeyError):
    pass


class UnknownURIError(KeyError):
    pass


jwt = JWTManager()
ma = Marshmallow()


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    mongo.init_app(app)

    ma.init_app(app)
    jwt.init_app(app)

    api = Api(app)

    from dtool_config_generator import generate_routes

    api.register_blueprint(TestResponseSchema.bp)

    @app.before_request
    def log_request():
        """Log the request header in debug mode."""
        app.logger.debug("Request Headers {}".format(request.headers))
        return None

    return app
