import logging

from flask import current_app, render_template, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer

from dtool_config_generator import db

from .extensions import mail

logger = logging.getLogger(__name__)


def require_confirmation(user):
    subject = f"Confirm new user {user.username}"
    ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    token = ts.dumps(user.id, salt='user-id-confirm-key')

    confirm_url = url_for(
        'auth.confirm',
        token=token,
        _external=True)

    user_confirmation_email_sender = current_app.config["USER_CONFIRMATION_EMAIL_SENDER"]
    user_confirmation_email_recipient = current_app.config["USER_CONFIRMATION_EMAIL_RECIPIENT"]

    html = render_template(
        'email/activate.html',
        username=user.username,
        confirm_url=confirm_url)

    # We'll assume that send_email has been defined in myapp/util.py
    # send_email(user_admin_email, subject, html)
    msg = Message(html=html,
                  subject=subject,
                  sender=user_confirmation_email_sender,
                  recipients=[user_confirmation_email_recipient])

    logger.debug("Send confirmation mail to %s", user_confirmation_email_recipient)
    mail.send(msg)


def confirm(user):
    """Confirm a new user. Usually, the admin confirms."""
    user.confirmed = True
    db.session.add(user)
    db.session.commit()
