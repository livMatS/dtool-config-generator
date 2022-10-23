""" Test auth routes"""
import pytest


pytestmark = pytest.mark.dockertest


def test_login_route_available(client):
    response = client.get("/auth/login")
    assert b"<h1>Log In</h1>" in response.data


def test_login_success(client):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "test_password",
    })
    # assert redirecting to home
    assert response.status_code == 302
    assert response.location == '/auth/home'


def test_login_failure(client):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrong_password",
    })

    # end up on login page again (with error)
    assert response.status_code == 200
    assert response.location is None
