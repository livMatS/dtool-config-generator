"""Test ldap service"""
from flask_ldap3_login import LDAP3LoginManager, AuthenticationResponseStatus


def test_ldap(ldap_service):
    ldap_manager = LDAP3LoginManager()
    ldap_manager.init_config(ldap_service)
    response = ldap_manager.authenticate('testuser', 'test_password')

    assert response.status == AuthenticationResponseStatus.success, "LDAP authentication failed."
