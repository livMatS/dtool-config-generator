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
