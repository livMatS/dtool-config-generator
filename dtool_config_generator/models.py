from dtool_config_generator import db

from flask_login import UserMixin


# Declare an Object Model for the user, and make it comply with the
# flask-login UserMixin mixin.
class User(UserMixin, db.Model):
    """User account model."""

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(256),
        index=True,
        unique=True
    )

    dn = db.Column(
        db.String(256),
        unique=True
    )

    activated = db.Column(
        db.Boolean(),
        nullable=False,
        default=True
    )

    confirmed = db.Column(
        db.Boolean(),
        nullable=False,
        default=False
    )

    # activated = db.Column(db.Boolean(), nullable=False, default=False)
    is_admin = db.Column(
        db.Boolean(),
        nullable=False,
        default=False
    )

    name = db.Column(
        db.String(256),
        unique=False
    )

    email = db.Column(
        db.String(256),
        unique=False
    )

    orcid = db.Column(
        db.String(256),
        unique=False
    )

    @property
    def is_active(self):
        return self.activated

    @property
    def is_confirmed(self):
        return self.confirmed
