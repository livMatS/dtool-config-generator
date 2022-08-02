from dtool_config_generator import ma
from dtool_config_generator import sql_db as db

from flask_login import UserMixin


# Declare an Object Model for the user, and make it comply with the
# flask-login UserMixin mixin.
class User(UserMixin,db.Model):
    """User account model."""
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(256),
        index=True,
        unique=True)

    dn = db.Column(
        db.String(256),
        unique=True)

    # activated = db.Column(db.Boolean(), nullable=False, default=False)
    is_admin = db.Column(
        db.Boolean(),
        nullable=False,
        default=False)

    name = db.Column(
        db.String(256),
        unique=False
    )

    email = db.Column(
        db.String(256),
        unique=True
    )