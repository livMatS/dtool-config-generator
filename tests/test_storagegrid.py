import json
import logging

logger = logging.getLogger(__name__)

from dtool_config_generator.comm.storagegrid import (
    authorize,
    create_user,
    create_s3_access_key_by_user_id,
    delete_s3_access_key_by_user_id_and_access_key,
    delete_user_by_id,
    get_user_by_short_name,
    get_user_by_id,
    list_users,
    list_s3_access_keys_by_user_id)


def test_storagegrid_authorize(production_app):
    with production_app.app_context():
        ret = authorize()
        logger.debug("Token: %s", ret)
        assert ret is not None


# @pytest.mark.skip(reason="User persists after creation.")
def test_storagegrid_create_user(production_app):
    with production_app.app_context():
        ret = create_user('user/test-user', 'Test User')
        logger.debug("User: %s", json.dumps(ret, indent=4))
        assert ret is not None


def test_storagegrid_list_users(production_app):
    with production_app.app_context():
        ret = list_users()
        logger.debug("Users: %s", json.dumps(ret, indent=4))
        assert ret is not None


def test_storagegrid_get_user_by_short_name(production_app):
    with production_app.app_context():
        ret = get_user_by_short_name('test-user')
        logger.debug("User: %s", json.dumps(ret, indent=4))
        assert ret is not None


def test_storagegrid_get_user_by_short_name(production_app):
    with production_app.app_context():
        ret_by_short_name = get_user_by_short_name('test-user')
        logger.debug("User: %s", json.dumps(ret_by_short_name, indent=4))
        assert ret_by_short_name is not None

        ret_by_id = get_user_by_id(ret_by_short_name['id'])
        logger.debug("User: %s", json.dumps(ret_by_id, indent=4))
        assert ret_by_id is not None

        assert ret_by_id == ret_by_short_name


def test_storagegrid_list_s3_access_keys_by_user_id(production_app):
    with production_app.app_context():
        ret_by_short_name = get_user_by_short_name('test-user')
        logger.debug("User: %s", json.dumps(ret_by_short_name, indent=4))
        assert ret_by_short_name is not None

        ret_by_id = list_s3_access_keys_by_user_id(ret_by_short_name['id'])
        logger.debug("S3 access keys: %s", json.dumps(ret_by_id, indent=4))
        assert ret_by_id is not None


# @pytest.mark.skip(reason="S3 access key persists after creation.")
def test_storagegrid_create_s3_access_key_by_user_id(production_app):
    with production_app.app_context():
        ret_by_short_name = get_user_by_short_name('test-user')
        logger.debug("User: %s", json.dumps(ret_by_short_name, indent=4))
        assert ret_by_short_name is not None

        import datetime
        timedelta = datetime.timedelta(days=1)
        ret_by_id = create_s3_access_key_by_user_id(ret_by_short_name['id'], timedelta)
        logger.debug("S3 access keys: %s", json.dumps(ret_by_id, indent=4))
        assert ret_by_id is not None


def test_storagegrid_delete_s3_access_key(production_app):
    with production_app.app_context():
        user = get_user_by_short_name('test-user')
        logger.debug("User: %s", json.dumps(user, indent=4))
        assert user is not None

        s3_acces_keys = list_s3_access_keys_by_user_id(user['id'])
        logger.debug("S3 access keys: %s", json.dumps(s3_acces_keys, indent=4))
        assert s3_acces_keys is not None

        for s3_access_key in s3_acces_keys:
            assert delete_s3_access_key_by_user_id_and_access_key(user['id'], s3_access_key['id'])


def test_storagegrid_delete_user(production_app):
    with production_app.app_context():
        user = get_user_by_short_name('test-user')
        logger.debug("User: %s", json.dumps(user, indent=4))
        assert user is not None

        assert delete_user_by_id(user['id'])