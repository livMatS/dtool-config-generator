from flask_login import current_user
from dtool_config_generator.extensions import db
from dtool_config_generator.security import confirm


def test_admin_route_success(client):
    with client:
        # log in
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "test_password",
        })
        assert response.status_code == 302
        confirm(current_user)

        db.session.commit()

        response = client.get("/admin/")

        assert response.status_code == 200
        assert response.location is None


def test_admin_route_failure(client):
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

        response = client.get("/admin/")

        assert response.status_code == 302
        assert response.location == '/auth/home'
