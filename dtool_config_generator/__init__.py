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
import click
import logging
import os

from flask import Flask, flash, redirect, request, url_for
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_smorest import Api

from dtool_config_generator.extensions import db, ma, mail
from dtool_config_generator.security import require_confirmation, confirm
from dtool_config_generator.utils import (
    TemplateContextBuilder,
    DtoolConfigGeneratorAdminIndexView)
from dtool_config_generator.config import Config


# settings from
# https://flask-ldap3-login.readthedocs.io/en/latest/quick_start.html

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
    except ImportError:
        logger.debug("All efforts to determine version failed.")
        __version__ = None


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


def create_app(test_config=None, test_config_file=None):
    app = Flask(__name__)

    CORS(app)

    # load the instance config, if it exists
    if test_config is None:
        app.config.from_object(Config)

        # override with config file specified in env variable
        if "FLASK_CONFIG_FILE" in os.environ:
            app.config.from_envvar("FLASK_CONFIG_FILE")
    else:
        # load the test config if passed in
        logger.debug("Inject test config %s", test_config)
        app.config.from_mapping(test_config)

        # override with config file specified in function call
        logger.debug("Override with config file %s", test_config_file)
        if test_config_file is not None:
            app.config.from_pyfile(test_config_file)

    mail.init_app(app)
    db.init_app(app)
    Migrate(app, db)
    ma.init_app(app)

    # admin initialized here due to https://github.com/flask-admin/flask-admin/issues/910
    admin = Admin(app, name=__name__,
                  index_view=DtoolConfigGeneratorAdminIndexView(),
                  template_mode='bootstrap3')

    from dtool_config_generator.models import User
    admin.add_view(ModelView(User, db.session))

    api = Api(app)

    login_manager = LoginManager(app)

    # Initialise the ldap manager using the settings read into the flask app.
    ldap_manager = LDAP3LoginManager(app)

    template_context_builder = TemplateContextBuilder(app)

    from dtool_config_generator import (
        auth_routes,
        config_routes,
        generate_routes,
        main_routes)

    api.register_blueprint(auth_routes.bp)
    api.register_blueprint(config_routes.bp)
    api.register_blueprint(generate_routes.bp)
    api.register_blueprint(main_routes.bp)

    from dtool_config_generator.utils import s3_access_credentials_as_context
    if app.config.get("STORAGEGRID_S3_CREDENTIALS_EMBEDDED_IN_CONFIG", False):
        template_context_builder.register(
            s3_access_credentials_as_context, name="s3_credentials")

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
        logger.debug("Entered ldap_manager.save_user for %s (%s; %s)", username, dn, data)
        uid_number = data.get("uidNumber")
        user_id = int(uid_number[0] if isinstance(uid_number, list) else uid_number)
        user = User.query.filter_by(id=user_id).first()

        if not user:
            logger.debug("User %s not yet recorded.", username)
            # the user has never logged in before and is created
            user = User(
                id=int(user_id),
                dn=dn,
                username=username
            )

            db.session.add(user)
            db.session.commit()

            # an activation email is sent to the admin
            require_confirmation(user)

        return user

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.before_first_request
    def enable_admin():
        admin_username = app.config.get("DTOOL_CONFIG_GENERATOR_ADMIN_USER_NAME", None)
        admin_userid = app.config.get("DTOOL_CONFIG_GENERATOR_ADMIN_USER_ID", None)

        if admin_username is None:
            logger.warning("No default admin username configured.")
            return

        if admin_userid is None:
            logger.warning("No default admin user id configured.")
            return

        admin_user = User.query.filter_by(id=admin_userid).first()
        if admin_user is None:
            logger.warning("Default admin user not in database. Create.")
            admin_user = User(id=admin_userid, username=admin_username)

        logger.debug("Confirm user %s.", admin_user.username)
        confirm(admin_user)

        logger.debug("Make user %s admin.", admin_user.username)
        admin_user.is_admin = True
        db.session.add(admin_user)
        db.session.commit()

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
