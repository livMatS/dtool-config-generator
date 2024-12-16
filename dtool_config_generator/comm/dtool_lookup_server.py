import logging
import yaml
from dtool_lookup_api.core.LookupClient import TokenBasedLookupClient, CredentialsBasedLookupClient

from asgiref.sync import async_to_sync
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
            lookup_url = current_app.config.get("DSERVER_URL")
        if auth_url is None:
            auth_url = current_app.config.get("DSERVER_TOKEN_GENERATOR_URL")
        if username is None:
            username = current_app.config.get("DSERVER_USERNAME")
        if password is None:
            password = current_app.config.get("DSERVER_PASSWORD")
        if verify_ssl is None:
            verify_ssl = current_app.config.get("DSERVER_VERIFY_SSL")

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


@async_to_sync
async def list_base_uris():
    """Get list of base URIs registered at lookup server."""
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        return await lookup_client.get_base_uris()


@async_to_sync
async def register_base_uri(base_uri):
    """Register base URI at lookup server."""
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        return await lookup_client.register_base_uri(base_uri)


@async_to_sync
async def permission_info(base_uri):
    """Get permissions info on base URI from lookup server."""
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        return await lookup_client.get_base_uri(base_uri)


@async_to_sync
async def grant_permissions(base_uri, username, allow_register=False):
    """Grant search or register permission on a base URI to user."""
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        base_uri_info = await lookup_client.get_base_uri(base_uri)
        if username not in base_uri_info['users_with_search_permissions']:
            base_uri_info['users_with_search_permissions'].append(username)
        if allow_register and username not in base_uri_info['users_with_register_permissions']:
            base_uri_info['users_with_register_permissions'].append(username)
        return await lookup_client.register_base_uri(
            base_uri,
            users_with_search_permissions=base_uri_info['users_with_search_permissions'],
            users_with_register_permissions=base_uri_info['users_with_register_permissions'])


@async_to_sync
async def revoke_permissions(base_uri, username, revoke_register=False):
    """Revoke search or register permissions on a base URI for user."""
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        base_uri_info = await lookup_client.get_base_uri(base_uri)
        if username in base_uri_info['users_with_search_permissions']:
            base_uri_info['users_with_search_permissions'].remove(username)
        if revoke_register and username in base_uri_info['users_with_register_permissions']:
            base_uri_info['users_with_register_permissions'].remove(username)
        return await lookup_client.register_base_uri(
            base_uri,
            users_with_search_permissions=base_uri_info['users_with_search_permissions'],
            users_with_register_permissions=base_uri_info['users_with_register_permissions'])


@async_to_sync
async def list_users():
    """Get list of users registered at lookup server."""
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        return await lookup_client.get_users()


@async_to_sync
async def user_info(username):
    """Show info on user registered at lookup server."""
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        return await lookup_client.get_user(username)


@async_to_sync
async def register_user(username, is_admin=False):
    async with CredentialsBasedLookupClientWithPersistentToken() as lookup_client:
        return await lookup_client.register_user(username, is_admin)
