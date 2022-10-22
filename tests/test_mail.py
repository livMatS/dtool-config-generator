"""Test mail service"""

import pytest
import smtplib

@pytest.mark.skip(reason="Needs a mailserver running locally.")
def test_smtp():
    with smtplib.SMTP("localhost", port=587) as smtp:
        assert smtp.login('admin@dtool.config.generator', 'password')

