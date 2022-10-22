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
import logging

from flask import abort, current_app, render_template, redirect, request, url_for
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import current_user, login_user, logout_user, login_required
from flask_smorest import Blueprint
from itsdangerous import URLSafeTimedSerializer

from .comm.dtool_lookup_server import register_user, grant_permissions
from .extensions import db
from .forms import ProfileForm
from .models import User
from .security import confirm as confirm_user

bp = Blueprint("auth", __name__, template_folder='templates', url_prefix='/auth')


logger = logging.getLogger(__name__)


# Declare some routes for usage to show the authentication process.
@bp.route('/home')
@login_required
def home():
    return render_template('auth/home.html')


@bp.route('/unconfirmed')
@login_required
def unconfirmed():
    return render_template('auth/unconfirmed.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Instantiate a LDAPLoginForm which has a validator to check if the user
    # exists in LDAP.
    form = LDAPLoginForm()

    if form.validate_on_submit():
        # Successfully logged in, We can now access the saved user object
        # via form.user.
        logger.debug(f"Authenticated user {form.user}")
        if request.form.get('remember'):
            login_user(form.user, remember=True)
        else:
            login_user(form.user)

        return redirect(url_for('auth.home'))  # Send them home

    return render_template('auth/login.html', form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# Declare some routes for usage to show the authentication process.

@bp.route('/confirm/<token>')
def confirm(token):
    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    user_id = ts.loads(token, salt="user-id-confirm-key", max_age=86400)

    user = User.query.filter_by(id=user_id).first_or_404()
    logger.debug("User %s confirmed.", user.username)
    confirm_user(user)

    if getattr(current_app.config, "DTOOL_LOOKUP_SERVER_REGISTER_USER_ON_CONFIRMATION", False):
        logger.debug("Register user %s at lookup server.", user.username)
        ret = register_user(user.username)
        if not ret:
            logger.warning("Registration of user '%s' at lookup server failed.", user.username)

    if getattr(current_app.config, "DTOOL_LOOKUP_GRANT_DEFAULT_SEARCH_PERMISSIONS_ON_CONFIRMATION", False):
        base_uris = getattr(current_app.config, "DTOOL_LOOKUP_DEFAULT_SEARCH_PERMISSIONS", [])
        if isinstance(base_uris, str):
            base_uris = [base_uris]

        logger.debug("Grant user '{}' search perissions on {}.".format(user.username, base_uris))
        for base_uri in base_uris:
            ret = grant_permissions(base_uri, user.username)
            if not ret:
                logger.warning("Granting search permissions on '%s' to user '%s' at lookup server failed.",
                               base_uri, user.username)

    return redirect(url_for('auth.home'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        logger.debug(f"Profile updated for user {current_user.username}")
        form.populate_obj(current_user)
        db.session.commit()

        return redirect(url_for('auth.home'))  # Send them home

    return render_template('auth/profile.html', form=form)
