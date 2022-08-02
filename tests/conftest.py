"""Test fixtures."""

import os
import pytest

from flask_ldap3_login import LDAP3LoginManager, AuthenticationResponseStatus

from dtool_config_generator.config import Config
from dtool_config_generator import create_app


class TestingConfig(Config):
    """Extend default config by testing settings."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

# ===============
# docker services
# ===============

@pytest.fixture(scope="session")
def ldap_config():
    config = dict()
    config["LDAP_HOST"]="ldap://localhost"
    config["LDAP_PORT"]=1389
    config["LDAP_USE_SSL"]=False
    config["LDAP_BASE_DN"]="dc=example,dc=org"
    config["LDAP_USER_DN"]="ou=users"
    config["LDAP_USER_RDN_ATTR"]="cn"
    config["LDAP_USER_LOGIN_ATTR"]="uid"
    config["LDAP_USER_OBJECT_FILTER"]="(objectclass=*)"
    config["LDAP_SEARCH_FOR_GROUPS"]=False
    config["LDAP_USER_SEARCH_SCOPE"]="SUBTREE"
    return config


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "tests", "compose", "docker-compose.yml")


@pytest.fixture(scope="session")
def ldap_service(docker_ip, docker_services, ldap_config):
    """Ensure that ldap service is up and responsive."""

    # Setup a LDAP3 Login Manager.
    ldap_manager = LDAP3LoginManager()
    # Init the mamager with the config since we aren't using an app
    ldap_manager.init_config(ldap_config)
    # Wat until service responsive, heck if the credentials are correct
    docker_services.wait_until_responsive(
        timeout=5.0, pause=1.0, check=lambda: ldap_manager.authenticate(
            'testuser', 'test_password').status == AuthenticationResponseStatus.success
    )
    return ldap_config


# =========
# flask app
# =========


@pytest.fixture(scope="session")
def flask_config_file(pytestconfig):
    return os.path.join(str(pytestconfig.rootdir), "tests", "etc", "flask_config.cfg")


@pytest.fixture(scope="session")
def test_config(ldap_config, pytestconfig):
    config = TestingConfig().to_dict()
    config.update(ldap_config)
    config["DTOOL_CONFIG_TEMPLATE"] = os.path.join(
        str(pytestconfig.rootdir), "tests", "templates", "dtool.json")
    config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    return config


@pytest.fixture()
def app(ldap_service, test_config):
    return create_app(test_config)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
