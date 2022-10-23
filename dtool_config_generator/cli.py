"""Command line utility functions."""

import pprint
import sys

import click
from flask import Flask
from flask.cli import AppGroup

from dtool_config_generator.models import User
from dtool_config_generator.utils import (
    sync_user,
    list_s3_access_keys,
    revoke_all_s3_access_keys,
    create_new_s3_access_key,
    revoke_and_regenerate_s3_access_credentials,
    sync_all_users_to_dtool_lookup_server
)

from dtool_config_generator.comm.dtool_lookup_server import (
    list_base_uris,
    list_users,
    register_base_uri,
    register_user,
    permission_info,
    grant_permissions,
    revoke_permissions,
    user_info)


from functools import wraps

app = Flask(__name__)

user_cli = AppGroup("user", help="User management commands.")
sg_cli = AppGroup("sg", help="StorageGRID key management commands.")
dls_cli = AppGroup("dls", help="dtool-lookup-server management commands.")


def user_from_username(f):
    """Turn username into User model."""
    @wraps(f)
    def decorated(username, *args, **kwargs):
        user = User.query.filter_by(id=username).first()
        if user is None:
            click.secho("User '{}' not in my database.".format(username), fg="red", err=True)
            user = User(username=username)

        return f(user, *args, **kwargs)
    return decorated


#############################################################################
# dtool-config-generator user commands
#############################################################################

@user_cli.command(name="list")
def cli_user_list():
    """Lists users in database."""
    user_list = User.query.all()
    if user_list is None:
        click.secho("Failed listing users.", fg="red", err=True)
        sys.exit(1)
    for user in user_list:
        pprint.pprint(user)


#############################################################################
# NetApp StorageGRID endpoint commands
#############################################################################

@sg_cli.command(name="sync")
@click.argument("username")
@user_from_username
def cli_sg_sync(user):
    """Syncs user entry to StorageGRID server."""

    sg_user_id = sync_user(user)
    if sg_user_id is None:
        click.secho("Failed syncinc user '{}' ".format(user.username), fg="red", err=True)
        sys.exit(1)
    click.secho("Synced user '{}': '{}'".format(user.username, sg_user_id))


@sg_cli.command(name="list")
@click.argument("username")
@user_from_username
def cli_sg_list_s3_access_keys(user):
    """Print all access keys of user."""
    user_list = list_s3_access_keys(user)
    if user_list is None:
        click.secho("Failed listing keys for user '{}' ".format(user.username), fg="red", err=True)
        sys.exit(1)
    pprint.pprint(user_list)


@sg_cli.command(name="revoke")
@click.argument("username")
@user_from_username
def cli_sg_revoke_all_s3_access_keys(user):
    """Revokes all s3 access keys attached to a user."""
    revoke_all_s3_access_keys(user)


@sg_cli.command(name="create")
@click.argument("username")
@user_from_username
def cli_sg_create_new_s3_access_key(user):
    """Creates new s3 access key - secret key pair attached to a user."""
    access_key, secret_key = create_new_s3_access_key(user)
    if access_key is None:
        click.secho("Failed creating access and secret key for user '{}' ".format(user.username), fg="red", err=True)
        sys.exit(1)
    click.secho("Access key '{}'".format(access_key))
    click.secho("Secret key '{}'".format(secret_key))


@sg_cli.command(name="recreate")
@click.argument("username")
@user_from_username
def cli_sg_revoke_and_regenerate_s3_access_credentials(user):
    """Revokes all access keys and generates a new pair."""
    access_key, secret_key = revoke_and_regenerate_s3_access_credentials(user)
    if access_key is None:
        click.secho("Failed recreating access and secret key for user '{}' ".format(user.username), fg="red", err=True)
        sys.exit(1)
    click.secho("Access key '{}'".format(access_key))
    click.secho("Secret key '{}'".format(secret_key))


#############################################################################
# dtool-lookup-server endpoint commands
#############################################################################

@dls_cli.group(name="base-uri")
def dls_base_uri():
    pass


@dls_base_uri.command(name="list")
def cli_dls_base_uri_list():
    """List base URIs registered at lookup server."""
    base_uris = list_base_uris()
    if base_uris is None:
        click.secho("Failed retrieving base URIs", fg="red", err=True)
        sys.exit(1)
    pprint.pprint(base_uris)


@dls_base_uri.command(name="register")
@click.argument("base_uri")
def cli_dls_base_uri_register(base_uri):
    """Register base URI at lookup server."""
    ret = register_base_uri(base_uri)
    if ret is None or not ret:
        click.secho("Failed registering base URI {}".format(base_uri), fg="red", err=True)
        sys.exit(1)


@dls_base_uri.command(name="info")
@click.argument("base_uri")
def cli_dls_base_uri_info(base_uri):
    """Show permissions info on base URI at lookup server."""
    base_uri_info = permission_info(base_uri)
    if base_uri_info is None:
        click.secho("Failed retrieving info on base URI {}".format(base_uri), fg="red", err=True)
        sys.exit(1)
    pprint.pprint(base_uri_info)


@dls_base_uri.command(name="allow")
@click.argument("base_uri")
@click.argument("username")
@click.option("--register", 'allow_register', is_flag=True, help="Allow registration of datasets as well.")
def cli_dls_base_uri_allow(base_uri, username, allow_register=False):
    """Grant search or register permission on a base URI to user."""
    ret = grant_permissions(base_uri, username, allow_register)
    if ret is None or not ret:
        click.secho("Failed updating permissions on base URI {}".format(base_uri), fg="red", err=True)
        sys.exit(1)


@dls_base_uri.command(name="revoke")
@click.argument("base_uri")
@click.argument("username")
@click.option("--register", 'revoke_register', is_flag=True, help="Revoke registration permission as well.")
def cli_dls_base_uri_revoke(base_uri, username, revoke_register=False):
    """Revoke search or register permissions on a base URI for user."""
    ret = revoke_permissions(base_uri, username, revoke_register)
    if ret is None or not ret:
        click.secho("Failed updating permissions on base URI {}".format(base_uri), fg="red", err=True)
        sys.exit(1)


@dls_cli.group(name="user")
def dls_user():
    pass


@dls_user.command(name="list")
def cli_dls_user_list():
    """List users registered at lookup server."""
    users = list_users()
    if users is None:
        click.secho("Failed retrieving users", fg="red", err=True)
        sys.exit(1)
    pprint.pprint(users)


@dls_user.command(name="info")
@click.argument("username")
def cli_dls_user_info(username):
    """Show info on user registered at lookup server."""
    user_info_dict = user_info(username)
    if user_info_dict is None:
        click.secho("Failed retrieving users", fg="red", err=True)
        sys.exit(1)
    pprint.pprint(user_info_dict)


@dls_user.command(name="register")
@click.argument("username")
@click.option('-a', '--admin', 'is_admin', is_flag=True, help="Register user as admin.")
def cli_dls_user_register(username, is_admin=False):
    """Register user at lookup server."""
    ret = register_user(username, is_admin)
    if ret is None or not ret:
        click.secho("Failed registering user {}".format(username), fg="red", err=True)
        sys.exit(1)


@dls_user.command(name="sync")
@click.option('-g', '--grant', 'grant_default_search_permissions',
              is_flag=True, help="Grant default search permissions.")
def cli_dls_user_sync(grant_default_search_permissions=False):
    """Create all users in db at lookup server and grant default search permissions if desired."""
    sync_all_users_to_dtool_lookup_server(grant_default_search_permissions)
