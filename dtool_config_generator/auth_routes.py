import logging

from flask import abort, current_app, render_template, redirect, request, url_for
from flask_ldap3_login.forms import LDAPLoginForm
from flask_login import current_user, login_user, logout_user, login_required
from flask_smorest import Blueprint
from itsdangerous import URLSafeTimedSerializer

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
