#
# Copyright 2022 Johannes Laurin Hörmann
#
# ### MIT license
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import os

import dtool_config_generator


_HERE = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = 'secret'
    # DEBUG = True

    DTOOL_CONFIG_TEMPLATE = os.path.join(os.path.dirname(__file__), 'templates', 'dtool.json')
    DTOOL_README_TEMPLATE = os.path.join(os.path.dirname(__file__), 'templates', 'dtool_readme.yml')

    USER_CONFIRMATION_EMAIL_SENDER = 'admin@dtool.config.generator'
    USER_CONFIRMATION_EMAIL_RECIPIENT = 'admin@dtool.config.generator'

    DTOOL_CONFIG_GENERATOR_ADMIN_USER_ID = 1000  # always sets this user as admin if exists
    DTOOL_CONFIG_GENERATOR_ADMIN_USER_NAME = 'testuser'  # always sets this user as admin if exists

    # dtool-lookup-server default options
    DTOOL_LOOKUP_SERVER_URL = 'http://localhost:5000'
    DTOOL_LOOKUP_SERVER_TOKEN_GENERATOR_URL = 'http://localhost:5001/token'
    DTOOL_LOOKUP_SERVER_USERNAME = 'testuser'
    DTOOL_LOOKUP_SERVER_PASSWORD = 'test_password'
    DTOOL_LOOKUP_SERVER_VERIFY_SSL = False

    # activating these will create a user and grant default permissions on the
    # lookup server side whenever the admin confirms a user
    DTOOL_LOOKUP_SERVER_REGISTER_USER_ON_CONFIRMATION = False
    DTOOL_LOOKUP_GRANT_DEFAULT_SEARCH_PERMISSIONS_ON_CONFIRMATION = False
    DTOOL_LOOKUP_DEFAULT_SEARCH_PERMISSIONS = ['s3://test-bucket', 'smb://test-share']

    # storagegrid s3 default options
    STORAGEGRID_HOST = 'localhost'
    STORAGEGRID_ACCOUNT_ID = '123456789'
    STORAGEGRID_USERNAME = 'admin'
    STORAGEGRID_PASSWORD = 'password'

    STORAGEGRID_DEFAULT_GROUP_UUID = None  # i.e. "00000000-0000-0000-0000-000000000000"

    STORAGEGRID_DEFAULT_S3_ACCESS_KEY_VALIDITY_PERIOD = 86400  # a day in seconds

    STORAGEGRID_S3_CREDENTIALS_EMBEDDED_IN_CONFIG = False

    # flask-admin default options
    FLASK_ADMIN_SWATCH = 'cerulean'

    # mail server default options
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 587
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    # MAIL_DEBUG = 'app.debug'
    MAIL_USERNAME = 'admin@dtool.config.generator'
    MAIL_PASSWORD = 'password'
    MAIL_DEFAULT_SENDER = 'admin@dtool.config.generator'
    # MAIL_MAX_EMAILS : default None
    MAIL_SUPPRESS_SEND = False  # : default app.testing
    # MAIL_ASCII_ATTACHMENTS : default False

    # ldap default options
    # Setup LDAP Configuration Variables. Change these to your own settings.
    # All configuration directives can be found in the documentation.

    # Hostname of your LDAP Server
    LDAP_HOST = "ldap://localhost"
    LDAP_PORT = 1389

    # Base DN of your directory
    LDAP_BASE_DN = "dc=example,dc=org"

    LDAP_USE_SSL = False

    # Users DN to be prepended to the Base DN
    LDAP_USER_DN = "ou=users"

    # Groups DN to be prepended to the Base DN
    # LDAP_GROUP_DN = 'ou=groups'

    # The RDN attribute for your user schema on LDAP
    LDAP_USER_RDN_ATTR = "cn"

    # The Attribute you want users to authenticate to LDAP with.
    LDAP_USER_LOGIN_ATTR = "uid"

    # The Username to bind to LDAP with
    # LDAP_BIND_USER_DN = None

    # The Password to bind to LDAP with
    # LDAP_BIND_USER_PASSWORD = None

    LDAP_USER_OBJECT_FILTER = "(objectclass=*)"
    LDAP_SEARCH_FOR_GROUPS = False
    LDAP_USER_SEARCH_SCOPE = "SUBTREE"

    JSONIFY_PRETTYPRINT_REGULAR = True

    # swagger default options
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

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///{}".format(os.path.join(_HERE, "..", "app.db")),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def to_lowercase_dict(cls):
        """Convert server configuration into dict for export."""
        exclusions = [
            "JWT_PRIVATE_KEY",
        ]  # config keys to exclude
        d = {"version": dtool_config_generator.__version__}
        for k, v in cls.__dict__.items():
            # select only capitalized fields
            if k.upper() == k and k not in exclusions:
                d[k.lower()] = v
        return d

    @classmethod
    def to_dict(cls):
        """Convert server configuration into dict."""
        d = {}
        for attribute in dir(cls):
            if attribute.upper() == attribute and attribute[0] != '_':
                d[attribute] = getattr(cls, attribute)
        return d
