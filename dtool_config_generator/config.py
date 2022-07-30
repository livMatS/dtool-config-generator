import os

import dtool_config_generator

_HERE = os.path.abspath(os.path.dirname(__file__))


def _get_file_content(key, default=""):
    file_path = os.environ.get(key, "")
    if os.path.isfile(file_path):
        content = open(file_path).read()
    else:
        content = ""
    return content


class Config(object):
    SECRET_KEY = 'secret'
    DEBUG = True

    # Setup LDAP Configuration Variables. Change these to your own settings.
    # All configuration directives can be found in the documentation.

    # Hostname of your LDAP Server
    LDAP_HOST = 'ad.mydomain.com'

    # Base DN of your directory
    # LDAP_BASE_DN = 'dc=mydomain,dc=com'

    # Users DN to be prepended to the Base DN
    # LDAP_USER_DN = 'ou=users'

    # Groups DN to be prepended to the Base DN
    # LDAP_GROUP_DN = 'ou=groups'

    # The RDN attribute for your user schema on LDAP
    # LDAP_USER_RDN_ATTR = 'cn'

    # The Attribute you want users to authenticate to LDAP with.
    # LDAP_USER_LOGIN_ATTR = 'mail'

    # The Username to bind to LDAP with
    # LDAP_BIND_USER_DN = None

    # The Password to bind to LDAP with
    # LDAP_BIND_USER_PASSWORD = None

    JSONIFY_PRETTYPRINT_REGULAR = True

    API_TITLE = "dtool-config-generator API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/doc"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = (
        "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"
    )
    OPENAPI_SWAGGER_UI_PATH = "/swagger"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    API_SPEC_OPTIONS = {
        "x-internal-id": "2"
    }

    @classmethod
    def to_dict(cls):
        """Convert server configuration into dict."""
        exclusions = [
            "JWT_PRIVATE_KEY",
        ]  # config keys to exclude
        d = {"version": dtool_config_generator.__version__}
        for k, v in cls.__dict__.items():
            # select only capitalized fields
            if k.upper() == k and k not in exclusions:
                d[k.lower()] = v
        return d

