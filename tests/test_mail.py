"""Test mail service"""

import pytest
import smtplib

from dtool_config_generator.utils import send_test_mail


@pytest.mark.skip(reason="Needs a mailserver running locally.")
def test_smtp():
    with smtplib.SMTP("localhost", port=587) as smtp:
        assert smtp.login('admin@dtool.config.generator', 'password')


@pytest.mark.skip(reason="Needs a mailserver running locally.")
def test_send_mail(production_app):
    with production_app.app_context():
        send_test_mail()

