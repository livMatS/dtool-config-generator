from dtool_config_generator.utils import (
    sync_user,
    create_new_s3_access_key,
    revoke_all_s3_access_keys,
    list_s3_access_keys,
    revoke_and_regenerate_s3_access_credentials
)

from dtool_config_generator.models import User


def test_revoke_and_regenerate_s3_access_credentials(production_app):
    with production_app.app_context():
        # user = get_user_by_short_name('test-user')
        test_user = User(
            username='test-user',
            name='Test User',
            email='test@dtool.config.generator'
        )

        access_key, secret_key = revoke_and_regenerate_s3_access_credentials(
            test_user)

        assert access_key is not None
        assert secret_key is not None

        s3_access_keys = list_s3_access_keys(test_user)

        assert isinstance(s3_access_keys, list)
        assert len(s3_access_keys) == 1

        revoke_all_s3_access_keys(test_user)
        s3_access_keys = list_s3_access_keys(test_user)

        assert isinstance(s3_access_keys, list)
        assert len(s3_access_keys) == 0
