import datetime
import json
import logging

from flask import current_app, flash, redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_login import current_user
from functools import wraps

import dtool_config_generator.comm.storagegrid as sg


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
    access_key, secret_key tuple
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
