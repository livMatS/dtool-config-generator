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
    create_new_s3_access_key
)

from functools import wraps

app = Flask(__name__)

user_cli = AppGroup("user", help="User management commands.")
sg_cli = AppGroup("sg", help="StorageGRID key management commands.")


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


@user_cli.command(name="list")
def cli_user_list():
    """Lists users in database."""
    user_list = User.query.all()
    if user_list is None:
        click.secho("Failed listing users.", fg="red", err=True)
        sys.exit(1)
    # click.secho("Synced user '{}': '{}'".format(user.username, sg_user_id))
    for user in user_list:
        pprint.pprint(user)


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
    access_key, secret_key = revoke_all_s3_access_keys(user)
    if access_key is None:
        click.secho("Failed recreating access and secret key for user '{}' ".format(user.username), fg="red", err=True)
        sys.exit(1)
    click.secho("Access key '{}'".format(access_key))
    click.secho("Secret key '{}'".format(secret_key))