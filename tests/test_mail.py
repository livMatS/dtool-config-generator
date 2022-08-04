"""Test mail service"""

import smtplib, ssl

from dtool_config_generator.utils import send_test_mail

def test_smtp():
    with smtplib.SMTP("localhost", port=587) as smtp:
        assert smtp.login('admin@dtool.config.generator', 'password')


def test_send_mail(production_app):
    with production_app.app_context():
        send_test_mail()

