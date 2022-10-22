import logging
import pytest


from dtool_config_generator.cli import (user_cli, sg_cli, dls_cli)


logger = logging.getLogger(__name__)


def test_cli_user_list(production_runner):
    result = production_runner.invoke(user_cli, args=['list'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_sg_list_s3_access_keys(production_runner):
    result = production_runner.invoke(sg_cli, args=['list', 'test-user'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_sg_create_new_s3_access_key(production_runner):
    result = production_runner.invoke(sg_cli, args=['create', 'test-user'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_sg_revoke_and_regenerate_s3_access_credentials(production_runner):
    result = production_runner.invoke(sg_cli, args=['recreate', 'test-user'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_sg_revoke_all_s3_access_keys(production_runner):
    result = production_runner.invoke(sg_cli, args=['revoke', 'test-user'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_dls_base_uri_list(production_runner):
    result = production_runner.invoke(dls_cli, args=['base-uri', 'list'])
    logger.debug(result.output)
    assert result.exit_code == 0


@pytest.mark.skip(reason="No way to undo registration of test base URI.")
def test_cli_dls_base_uri_register(production_runner):
    result = production_runner.invoke(dls_cli, args=['base-uri', 'register', 'test://base/uri'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_dls_base_uri_info(production_runner):
    result = production_runner.invoke(dls_cli, args=['base-uri', 'info', 's3://test-bucket'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_dls_base_uri_allow(production_runner):
    result = production_runner.invoke(dls_cli, args=['base-uri', 'allow', 's3://test-bucket', 'testuser'])
    logger.debug(result.output)
    assert result.exit_code == 0


@pytest.mark.skip(reason="No way to undo modification to production system.")
def test_cli_dls_base_uri_revoke(production_runner):
    result = production_runner.invoke(dls_cli, args=['base-uri', 'revoke', 's3://test-bucket', 'testuser'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_dls_user_list(production_runner):
    result = production_runner.invoke(dls_cli, args=['user', 'list'])
    logger.debug(result.output)
    assert result.exit_code == 0


def test_cli_dls_user_info(production_runner):
    result = production_runner.invoke(dls_cli, args=['user', 'info', 'testuser'])
    logger.debug(result.output)
    assert result.exit_code == 0


def cli_dls_user_register(production_runner):
    result = production_runner.invoke(dls_cli, args=['user', 'register', 'testuser'])
    logger.debug(result.output)
    assert result.exit_code == 0
