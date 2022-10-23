"""Test web app basic responses."""
import pytest

import json
import logging

from flask_login import current_user
from dtool_config_generator.security import confirm
from dtool_config_generator.extensions import db


pytestmark = pytest.mark.dockertest


logger = logging.getLogger(__name__)


def test_config_route_success(client):
    with client:
        # log in
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "test_password",
        })
        assert response.status_code == 302

        confirm(current_user)

        current_user.is_admin = True
        db.session.commit()

        response = client.get("/config/info")
        logger.debug(json.dumps(response.json, indent=4))
        assert response.status_code == 200
        assert isinstance(response.json, dict)


def test_config_route_failure(client):
    with client:
        # log in
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "test_password",
        })
        assert response.status_code == 302

        confirm(current_user)
        current_user.is_admin = False  # invalidate admin rights
        db.session.commit()

        # user is not admin

        response = client.get("/config/info")
        assert response.status_code == 302
        assert response.json is None
