"""Test mail service"""

import smtplib, ssl


def test_smtp():
    with smtplib.SMTP("localhost", port=587) as smtp:
        assert smtp.login('admin@dtool.config.generator', 'password')

