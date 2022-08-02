import click
import logging
import os

from flask import Flask, flash, redirect, request, url_for
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_smorest import Api

from dtool_config_generator.extensions import db, ma, admin
from dtool_config_generator.models import User

# settings from
# https://flask-ldap3-login.readthedocs.io/en/latest/quick_start.html

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# workaround for diverging python versions:
try:
    from importlib.metadata import version, PackageNotFoundError
    logger.debug("imported version, PackageNotFoundError from importlib.metadata")
except ModuleNotFoundError:
    from importlib_metadata import version, PackageNotFoundError
    logger.debug("imported version, PackageNotFoundError from importlib_metadata")

# first, try to determine dynamic version at runtime
try:
    __version__ = version(__name__)
    logger.debug("Determined version %s via importlib_metadata.version", __version__)
except PackageNotFoundError:
    # if that fails, check for static version file written by setuptools_scm
    try:
        from .version import version as __version__
        logger.debug("Determined version %s from autogenerated dtool_lookup_gui/version.py", __version__)
    except:
        logger.debug("All efforts to determine version failed.")
        __version__ = None


from dtool_config_generator.config import Config


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


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    # load the instance config, if it exists
    if  test_config is None:
        app.config.from_object(Config)

        # override with config file specified in env variable
        if "FLASK_CONFIG_FILE" in os.environ:
            app.config.from_envvar("FLASK_CONFIG_FILE")
    else:
        # load the test config if passed in
        logger.debug(f"Inject test config %s" % test_config)
        app.config.from_mapping(test_config)

    db.init_app(app)
    Migrate(app, db)
    ma.init_app(app)
    admin.init_app(app)

    admin.add_view(ModelView(User, db.session))

    api = Api(app)

    login_manager = LoginManager(app)

    # Initialise the ldap manager using the settings read into the flask app.
    ldap_manager = LDAP3LoginManager(app)

    from dtool_config_generator import (
        config_routes,
        generate_routes,
        auth_routes,
        main_routes)

    api.register_blueprint(generate_routes.bp)
    api.register_blueprint(auth_routes.bp)
    api.register_blueprint(config_routes.bp)

    @login_manager.unauthorized_handler
    def unauthorized():
        """Redirect unauthorized users to Login page."""
        flash('You must be logged in to view that page.')
        return redirect(url_for('auth.login'))

    # https://github.com/nickw444/flask-ldap3-login/issues/26
    # Declare a User Loader for Flask-Login.
    # Simply returns the User if it exists in our 'database', otherwise
    # returns None.
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter_by(id=user_id).first()

    # Declare The User Saver for Flask-Ldap3-Login
    # This method is called whenever a LDAPLoginForm() successfully validates.
    # Here you have to save the user, and return it so it can be used in the
    # login controller.
    @ldap_manager.save_user
    def save_user(dn, username, data, memberships):
        uidNumber = data.get("uidNumber")
        user_id = int(uidNumber[0] if isinstance(uidNumber, list) else uidNumber)
        user = User.query.filter_by(id=user_id).first()

        if not user:
            user = User(
                id=int(user_id),
                dn=dn,
                username=username
            )
            db.session.add(user)
            db.session.commit()

        return user

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.before_request
    def log_request():
        """Log the request header in debug mode."""
        app.logger.debug("Request Headers {}".format(request.headers))
        return None

    #############################################################################
    # Command line helper utilities.
    #############################################################################

    @app.cli.command()
    @click.argument('username')
    @click.option('--password', prompt=True, hide_input=True)
    def test_authentication(username, password):
        """Test authentication."""
        ldap_response = ldap_manager.authenticate(username, password)
        print(ldap_response.status)

    return app
