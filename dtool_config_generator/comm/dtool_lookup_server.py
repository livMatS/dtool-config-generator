
import json
import logging
import requests
import datetime
from dtool_lookup_api.core.LookupClient import TokenBasedLookupClient, CredentialsBasedLookupClient

from flask import current_app


logger = logging.getLogger(__name__)


token = None


class CredentialsBasedLookupClientWithPersistentToken(CredentialsBasedLookupClient):
    """"Caches valid token as class attribute without storing dtool config file."""
    _token = None

    @property
    def token(self):
        return type(self)._token

    @token.setter
    def token(self, value):
        type(self)._token = value

    def __init__(self,
                 lookup_url=None,
                 auth_url=None,
                 username=None,
                 password=None,
                 verify_ssl=None):

        if lookup_url is None:
            lookup_url = current_app.config.get("DTOOL_LOOKUP_SERVER_URL")
        if auth_url is None:
            auth_url = current_app.config.get("DTOOL_LOOKUP_SERVER_TOKEN_GENERATOR_URL")
        if username is None:
            username = current_app.config.get("DTOOL_LOOKUP_SERVER_USERNAME")
        if password is None:
            password = current_app.config.get("DTOOL_LOOKUP_SERVER_PASSWORD")
        if verify_ssl is None:
            verify_ssl = current_app.config.get("DTOOL_LOOKUP_SERVER_VERIFY_SSL")

        logger.debug("Initializing %s with lookup_url=%s, auth_url=%s, username=%s, ssl=%s",
                     type(self).__name__, lookup_url, auth_url, username, verify_ssl)

        super().__init__(
            lookup_url=lookup_url,
            auth_url=auth_url,
            username=username,
            password=password,
            verify_ssl=verify_ssl)

        logger.debug("%s initialized with lookup_url=%s, auth_url=%s, username=%s, ssl=%s",
                     type(self).__name__, self.lookup_url, self.auth_url,
                     self.username, self.verify_ssl)

    async def connect(self):
        """Establish connection."""
        if await self.has_valid_token():
            logger.debug("Reusing provided token.")
            await TokenBasedLookupClient.connect(self)
        else:
            logger.debug("Requesting new token.")
            await CredentialsBasedLookupClient.connect(self)

    # TODO: Replace with something more elegant.
    async def has_valid_token(self):
        """Determine whether token still valid."""
        if self.token is None or self.token == "":
            logger.debug("Token empty.")
            return False
        else:
            logger.debug("Testing token validity via /config/info route.")
            async with self.session.get(
                    f'{self.lookup_url}/config/info',
                    headers=self.header,
                    ssl=self.verify_ssl) as r:
                status_code = r.status
                text = await r.text()
            logger.debug("Server answered with %s: %s.", status_code, yaml.safe_load(text))
            return status_code == 200