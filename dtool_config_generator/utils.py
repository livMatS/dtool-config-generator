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
import datetime
import json
import logging

from flask import current_app, flash, redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_login import current_user
from flask_mail import Message
from functools import wraps

from dtool_config_generator.extensions import mail

import dtool_config_generator.comm.storagegrid as sg
import dtool_config_generator.comm.dtool_lookup_server as dls

from dtool_config_generator.models import User


DEFAULT_S3_ACCESS_KEY_VALIDITY_PERIOD = 86400

logger = logging.getLogger(__name__)


# inspired by https://github.com/flask-admin/flask-admin/blob/master/examples/auth-flask-login/app.py
# Create customized index view class that handles login & registration
class DtoolConfigGeneratorAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            flash('You need to be logged in.')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('You need to be admin.')
            return redirect(url_for('auth.home'))
        return super().index()


class TemplateContextBuilder():
    """Builds """
    def __init__(self, app=None):
        self._func_dict = {}

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Configures an application. This registers an `after_request` call, and
        attaches this `LoginManager` to it as `app.login_manager`.
        :param app: The :class:`flask.Flask` object to configure.
        :type app: :class:`flask.Flask`
        :param add_context_processor: Whether to add a context processor to
            the app that adds a `current_user` variable to the template.
            Defaults to ``True``.
        :type add_context_processor: bool
        """
        app.template_context_builder = self

    def register(self, func, name=None):
        """Register a context builder function.

        Parameters
        ----------
        func: a function with some return value
        name: a unique name for the context attribute, per default name of func
        """
        if name is None:
            name = func.__name__
        if name in self._func_dict:
            raise ValueError("'%s' already registered.", name)
        self._func_dict[name] = func

    def run(self, *args, **kwargs):
        return {
            name: func(*args, **kwargs) for name, func in self._func_dict.items()}


def send_test_mail():
    """Send test mail"""
    subject = f"Test mail."

    user_confirmation_email_sender = current_app.config["USER_CONFIRMATION_EMAIL_SENDER"]
    user_confirmation_email_recipient = current_app.config["USER_CONFIRMATION_EMAIL_RECIPIENT"]

    msg = Message(body='Hello!',
                  subject=subject,
                  sender=user_confirmation_email_sender,
                  recipients=[user_confirmation_email_recipient])

    logger.debug("Send test mail to %s", user_confirmation_email_recipient)
    mail.send(msg)


def confirmation_required(func):
    """
    If you decorate a view with this, it will ensure that the current user has
    been confirmed before calling the actual view. (If they are not, it calls
    the :attr:`LoginManager.unauthorized` callback.) For
    example::
        @app.route('/post')
        @login_required
        @confirmation_required
        def post():
            pass
    If there are only certain times you need to require that your user is
    logged in, you can do so with::
        if not current_user.is_confirmed:
            return current_app.login_manager.unauthorized()
    ...which is essentially the code that this function adds to your views.
    It can be convenient to globally turn off requiring confirmation when unit
    testing. To enable this, if the application configuration variable
    `CONFIRMATION_DISABLED` is set to `True`, this decorator will be ignored.
    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("CONFIRMATION_DISABLED"):
            pass
        elif not current_user.is_confirmed:
            return redirect(url_for('auth.unconfirmed'))

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view


def admin_required(func):
    """
    :param func: The view function to decorate.
    :type func: function
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("ADMIN_DISABLED"):
            pass
        elif not current_user.is_admin:
            return current_app.login_manager.unauthorized()

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view


#############################################################################
# NetApp StorageGRID endpoint utility functions
#############################################################################

def sync_user(user):
    """Syncs user entry to StorageGRID server

    Returns
    -------
    StorageGRID user id or None for failure."""
    sg_user = sg.get_user_by_short_name(user.username)
    if sg_user is None:
        logger.debug("User %s does not exist on StorageGRID, create.")

        member_of = current_app.config.get('STORAGEGRID_DEFAULT_GROUP_UUID', None)
        if member_of is not None:
            member_of = [member_of]

        sg_user = sg.create_user(
            unique_name=f'user/{user.username}',
            full_name=user.name,
            member_of=member_of)

        if sg_user is None:
            logger.error("Sync user failed.")
            return None

    return sg_user["id"]


def list_s3_access_keys(user):
    user_id = sync_user(user)
    return sg.list_s3_access_keys(user_id)


def revoke_all_s3_access_keys(user):
    """Revokes all s3 access keys attached to a user."""
    user_id = sync_user(user)
    s3_access_keys = sg.list_s3_access_keys(user_id)
    if s3_access_keys is None:
        logger.debug("User %s has no access keys")
        return

    for s3_access_key in s3_access_keys:
        if not sg.delete_s3_access_key(
                user_id=user_id, access_key=s3_access_key["id"]):
            logger.error("Failed deleting s3 access key %s for user %s",
                         s3_access_key["id"], user.username)
        else:
            logger.debug("Deleted s3 access key %s for user %s",
                         s3_access_key["id"], user.username)


def create_new_s3_access_key(user):
    """Creates new s3 access key - secret key pair attached to a user.

    Returns
    -------
    access_key, secret_key tuple or None, None on failure
    """
    seconds = int(current_app.config.get(
        'STORAGEGRID_DEFAULT_S3_ACCESS_KEY_VALIDITY_PERIOD',
        DEFAULT_S3_ACCESS_KEY_VALIDITY_PERIOD))
    timedelta = datetime.timedelta(seconds=seconds)

    user_id = sync_user(user)
    if user_id is None:
        return None, None
    s3_access_key = sg.create_s3_access_key(user_id=user_id, timedelta=timedelta)

    return s3_access_key["accessKey"], s3_access_key["secretAccessKey"]


def revoke_and_regenerate_s3_access_credentials(user):
    """Revokes all currently active access keys and generates a new pair.

    Returns
    -------
    access_key, secret_key tuple"""

    sync_user(user)
    revoke_all_s3_access_keys(user)
    return create_new_s3_access_key(user)


def s3_access_credentials_as_context():
    """Returns new credentials as dict"""
    access_key, secret_access_key = revoke_and_regenerate_s3_access_credentials(current_user)
    return {"access_key": access_key, "secret_access_key": secret_access_key}


#############################################################################
# dtool-lookup-server endpoint utility functions
#############################################################################


def sync_all_users_to_dtool_lookup_server(grant_default_search_permissions=None,
                                          default_search_permissions=None):
    """Create all users in db at lookup server.

    Parameters
    ----------
    grant_default_search_permissions: bool, default True
        Grant grant synced users default search permissions.
    default_search_permissions: list of str, default None
        List of base URI to grant synced users search permissions to.
        Will look up DTOOL_LOOKUP_DEFAULT_SEARCH_PERMISSIONS config value.
    """

    dcg_user_list = [user.username for user in User.query.all()]
    dls_user_list = [user['username'] for user in dls.list_users()]

    base_uris = current_app.config.get('DTOOL_LOOKUP_DEFAULT_SEARCH_PERMISSIONS', [])
    if isinstance(base_uris, str):
        base_uris = [base_uris]

    for username in dcg_user_list:
        logger.debug("Processing user '{}'.".format(username))
        if username not in dls_user_list:
            logger.debug("Register user '{}'.".format(username))
            dls.register_user(username)
        else:
            logger.debug("User '{}' already registered.".format(username))
        if grant_default_search_permissions:
            logger.debug("Grant user '{}' search perissions on {}.".format(username, base_uris))
            for base_uri in base_uris:
                dls.grant_permissions(base_uri, username)
