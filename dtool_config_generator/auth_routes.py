import logging

from flask import render_template, redirect, url_for
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import current_user, login_user, logout_user, login_required
from flask_smorest import Blueprint

bp = Blueprint("auth", __name__, template_folder='templates', url_prefix='/auth')


logger = logging.getLogger(__name__)

# Declare some routes for usage to show the authentication process.
@bp.route('/home')
def home():
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('auth.login'))

    return render_template('auth/home.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Instantiate a LDAPLoginForm which has a validator to check if the user
    # exists in LDAP.
    form = LDAPLoginForm()

    if form.validate_on_submit():
        # Successfully logged in, We can now access the saved user object
        # via form.user.
        logger.debug(f"Authenticated user {form.user}")
        login_user(form.user)  # Tell flask-login to log them in.
        return redirect(url_for('auth.home'))  # Send them home

    return render_template('auth/login.html', form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
