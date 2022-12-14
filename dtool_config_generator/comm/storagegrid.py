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
import json
import logging
import requests
import datetime

from flask import current_app


logger = logging.getLogger(__name__)


token = None


def authorize():
    """Returns a valid token in case of success, otherwise None."""
    host = current_app.config.get("STORAGEGRID_HOST")
    account_id = current_app.config.get("STORAGEGRID_ACCOUNT_ID")
    username = current_app.config.get("STORAGEGRID_USERNAME")
    password = current_app.config.get("STORAGEGRID_PASSWORD")

    url = f'https://{host}/api/v3/authorize'

    logger.debug("Authorize via %s", url)

    request_data = {
        "accountId": account_id,
        "username": username,
        "password": password,
        "cookie": True,
        "csrfToken": False
    }

    response = requests.post(url, json=request_data)
    # sample response.json:
    # {
    #     "responseTime": "2022-08-02T22:34:41.141Z",
    #     "status": "success",
    #     "apiVersion": "3.4",
    #     "data": "0e12464b-8c30-44bd-bbd6-a1588a202d7b"
    # }
    response_data = response.json()
    if response_data.get("status") == "success":
        logger.debug("Authorization successful.")
        return response_data.get("data", None)
    else:
        logger.warning("Authorization failed.")
        logger.debug(json.dumps(
            response_data, indent=4))
        return None


def check_token(token):
    """Check validity of token for NetApp STorageGRID endpoint.

    Parameters
    ----------
    token: string, default None
        if None, use cached global token

    Returns
    -------
    bool
    """


    host = current_app.config.get("STORAGEGRID_HOST")

    # use access-restricted config route to check health
    url = f'https://{host}/api/v3/org/config'

    logger.debug("Check token via %s", url)

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url, headers=headers)
    # sample response:
    # {
    #     'responseTime': '2022-10-23T19:14:21.636Z',
    #     'status': 'success',
    #     'apiVersion': '3.4',
    #     'data': {
    #         'auto-logout': 9000,
    #         'user': {
    #             'id': 'ec520845-ee41-4158-8bc3-79dbf1473246',
    #             'username': 'test-user',
    #             'uniqueName': 'user/test-user',
    #             'firstName': 'Test',
    #             'fullName': 'Test USer',
    #             'federated': False},
    #             'token': {'expires': '2022-10-24T11:14:21.000Z'},
    #             'permissions': {'rootAccess': True},
    #             'deactivatedFeatures': {},
    #             'account': {
    #                 'id': '80888526281258163394',
    #                 'name': 'frct-test',
    #                 'capabilities': ['management', 's3'],
    #                 'policy': {
    #                     'useAccountIdentitySource': True,
    #                     'allowPlatformServices': True,
    #                     'allowSelectObjectContent': False,
    #                     'quotaObjectBytes': 10000000000000
    #                 }
    #             },
    #         'restrictedPort': False
    #     }
    # }
    return response.status_code == 200


def headers():
    global token
    # get new token if no token cached or token not valid anymore
    if token is None or not check_token(token):
        token = authorize()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    return headers


def list_users(limit=25, **kwargs):
    """List users.

    Parameters
    ----------
    type: string
        filter by user type 'local' or 'federated'
    limit: int
        maximum number of results
    marker: string
        marker-style pagination offset (value is User's URN)
    includeMarker: bool
        if set, the marker element is also returned
    order: string
        'asc' or 'desc'

    Returns
    -------
    list of dict or None
    """
    host = current_app.config.get("STORAGEGRID_HOST")

    params = {'limit': limit, **kwargs}

    url = f'https://{host}/api/v3/org/users'

    logger.debug("List users via %s", url)

    response = requests.get(url, params=params, headers=headers())
    response_data = response.json()
    if response_data.get("status") == "success":
        logger.debug("Listing users successful.")
        return response_data.get("data", None)
    else:
        logger.warning("Listing users failed.")
        logger.debug(json.dumps(
            response_data, indent=4))
        return None


def get_user_by_short_name(short_name):
    """Get user by short name.

    Parameters
    ----------
    short_name: string
        uniqueName minus prefix, i.e. jh1130

    Returns
    -------
    dict or None
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/org/users/user/{short_name}'

    logger.debug("Query user via %s", url)

    response = requests.get(url, headers=headers())
    response_data = response.json()
    # sample response:
    # {
    #     "id": "68467f87-d617-42fa-b507-9b8ea7616d42",
    #     "accountId": "80888526281258163391",
    #     "fullName": "Johannnes Laurin Hörmann",
    #     "uniqueName": "user/jh1130",
    #     "userURN": "urn:sgws:identity::80888526281258163393:user/jh1130",
    #     "federated": false,
    #     "memberOf": [
    #       "2d9bce8d-5512-4dd7-93de-f266e1c4b76a"
    #     ],
    #     "disable": false
    #   }
    if response_data.get("status") == "success":
        logger.debug("User query successful.")
        return response_data.get("data", None)
    else:
        logger.warning("User query failed.")
        logger.debug(json.dumps(
            response_data, indent=4))
        return None


def get_user_by_id(id):
    """Get user by id.

    Parameters
    ----------
    id: string (uuid)
        user id

    Returns
    -------
    dict
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/org/users/{id}'

    logger.debug("Query user via %s", url)

    response = requests.get(url, headers=headers())
    response_data = response.json()
    # sample response:
    # {
    #     "id": "68467f87-d617-42fa-b507-9b8ea7616d42",
    #     "accountId": "80888526281258163391",
    #     "fullName": "Johannnes Laurin Hörmann",
    #     "uniqueName": "user/jh1130",
    #     "userURN": "urn:sgws:identity::80888526281258163393:user/jh1130",
    #     "federated": false,
    #     "memberOf": [
    #       "2d9bce8d-5512-4dd7-93de-f266e1c4b76a"
    #     ],
    #     "disable": false
    #   }
    if response_data.get("status") == "success":
        logger.debug("User query successful.")
        return response_data.get("data", None)
    else:
        logger.warning("User query failed.")
        logger.debug(json.dumps(
            response_data, indent=4))
        return None


def check_health():
    """Check health of NetApp STorageGRID endpoint.

    Returns
    -------
    bool
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/versions'


    logger.debug("Check health via %s", url)

    response = requests.get(url)
    # response_data = response.json()
    # sample response:
    # {'responseTime': '2022-10-23T19:02:50.082Z', 'status': 'success', 'apiVersion': '3.4', 'data': [2, 3]}
    return response.status_code == 200


def create_user(unique_name, full_name, member_of=None, disable=False):
    """Create new user.

    Parameters
    ----------
    unique_name: string, i.e. user/jh1130
        the machine-readable name for the User (unique within an Account; must begin with user/ or federated-user/).
        The portion after the slash is the "username" that is used to sign in.
    full_name: string
        the human-readable name for the User (required for local Users and imported automatically for federated Users)
    member_of: list of strings (uuids), default: None
        Group memberships for this User (required for local Users and imported automatically for federated Users)
    disable: bool default: False,
        if true, the local User cannot sign in (does not apply to federated Users)

    Returns
    -------
    dict or None
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/org/users'

    request_data = {
        'uniqueName': unique_name,
        'fullName': full_name
    }
    if member_of is not None:
        request_data['memberOf'] = member_of
    if disable:
        request_data['disable'] = True

    logger.debug("Create new user via %s", url)

    response = requests.post(url, json=request_data, headers=headers())
    response_data = response.json()
    # sample response:
    # {
    #     "id": "2803cbde-b2fa-4e6e-b756-c3194ed1d6e7",
    #     "accountId": "80888526281258163395",
    #     "fullName": "Test User",
    #     "uniqueName": "user/ATestUser",
    #     "userURN": "urn:sgws:identity::80888526281258163395:user/ATestUser",
    #     "federated": false,
    #     "memberOf": null,
    #     "disable": false
    #   }
    if response_data.get("status") == "success":
        logger.debug("User creation successful.")
        return response_data.get("data", None)
    else:
        logger.warning("User creation failed.")
        logger.debug(json.dumps(
            response_data, indent=4))
        return None


def delete_user(id):
    """Get user by id.

    Parameters
    ----------
    id: string (uuid)
        user id

    Returns
    -------
    bool
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/org/users/{id}'

    logger.debug("Delete user via %s", url)

    response = requests.delete(url, headers=headers())
    return response.status_code == 204


def list_s3_access_keys(user_id):
    """List s3 access keys for user id.

    Parameters
    ----------
    user_id: string (uuid)
        user id

    Returns
    -------
    list of dict or None
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/org/users/{user_id}/s3-access-keys'

    logger.debug("List s3 access keys for user via %s", url)

    response = requests.get(url, headers=headers())
    response_data = response.json()
    # sample response:
    # [
    #     {
    #       "id": "abcABC_01234-0123456789abcABCabc0123456789==",
    #       "accountId": 12345678901234567000,
    #       "displayName": "****************AB12",
    #       "userURN": "urn:sgws:identity::12345678901234567890:root",
    #       "userUUID": "00000000-0000-0000-0000-000000000000",
    #       "expires": "2020-09-04T00:00:00.000Z"
    #     }
    #   ]
    if response_data.get("status") == "success":
        logger.debug("Listing s3 access keys successful.")
        return response_data.get("data", None)
    else:
        logger.warning("Listing s3 access keys failed.")
        logger.debug(json.dumps(
            response_data, indent=4))
        return None


def _create_s3_access_key(user_id, expires):
    """Create s3 access key for user id.

    Parameters
    ----------
    user_id: string (uuid)
        user id
    expires: string (iso format datetime)
        i.e. "2020-09-04T00:00:00.000Z"

    Returns
    -------
    dict
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/org/users/{user_id}/s3-access-keys'

    request_data = {
        'expires': expires
    }

    logger.debug("Create s3 access keys for user via %s", url)

    response = requests.post(url, json=request_data, headers=headers())
    response_data = response.json()
    # sample response:
    #  {
    #     "id": "abcABC_01234-0123456789abcABCabc0123456789==",
    #     "accountId": 12345678901234567000,
    #     "displayName": "****************AB12",
    #     "userURN": "urn:sgws:identity::12345678901234567890:root",
    #     "userUUID": "00000000-0000-0000-0000-000000000000",
    #     "expires": "2020-09-04T00:00:00.000Z",
    #     "accessKey": "ABCDEFabcd1234567890",
    #     "secretAccessKey": "abcABC+123456789012345678901234567890123"
    #   }
    if response_data.get("status") == "success":
        logger.debug("S3 access key creation successful.")
        return response_data.get("data", None)
    else:
        logger.warning("S3 access key creation failed.")
        logger.debug(json.dumps(
            response_data, indent=4))
        return None


def create_s3_access_key(user_id, timedelta):
    """
    Create s3 access key for user id.

    Parameters
    ----------
    user_id: string (uuid)
        user id
    timedelta: datetime.timedelta
        specify expiry date as timedelta from now on
    Returns
    -------
    dict
    """

    expiry_date = datetime.datetime.now() + timedelta
    return _create_s3_access_key(user_id, expiry_date.isoformat())


def delete_s3_access_key(user_id, access_key):
    """Delete s3 access key by user id and access key

    Parameters
    ----------
    user_id: string (uuid)
        user id
    access_key: string

    Returns
    -------
    bool
    """

    host = current_app.config.get("STORAGEGRID_HOST")

    url = f'https://{host}/api/v3/org/users/{user_id}/s3-access-keys/{access_key}'

    logger.debug("Delete s3 access key via %s", url)

    response = requests.delete(url, headers=headers())
    return response.status_code == 204
