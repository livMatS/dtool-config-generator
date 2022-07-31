"""Test configuration generation routes"""

DTOOL_CONFIG = {
  "DTOOL_LOOKUP_SERVER_TOKEN_GENERATOR_URL": "https://localhost:5001/token",
  "DTOOL_LOOKUP_SERVER_URL": "https://localhost:5000/lookup",
  "DTOOL_LOOKUP_SERVER_USERNAME": "testuser",
  "DTOOL_LOOKUP_SERVER_VERIFY_SSL": "false",
  "DTOOL_S3_ACCESS_KEY_ID_test-bucket": "testuser_access_key",
  "DTOOL_S3_DATASET_PREFIX": "u/testuser/",
  "DTOOL_S3_ENDPOINT_test-bucket": "http://localhost:9000",
  "DTOOL_S3_SECRET_ACCESS_KEY_test-bucket": "testuser_secret_key",
  "DTOOL_SMB_DOMAIN_test-share": "WORKGROUP",
  "DTOOL_SMB_PASSWORD_test-share": "a-guest-needs-no-password",
  "DTOOL_SMB_PATH_test-share": "dtool",
  "DTOOL_SMB_SERVER_NAME_test-share": "localhost",
  "DTOOL_SMB_SERVER_PORT_test-share": 4445,
  "DTOOL_SMB_SERVICE_NAME_test-share": "sambashare",
  "DTOOL_SMB_USERNAME_test-share": "guest",
  "DTOOL_USER_EMAIL": "test@mail.com",
  "DTOOL_USER_FULL_NAME": "Test User"
}


def test_generate_config_success(client):
    with client:
        # log in
        response = client.post("/auth/login", data={
            "username": "testuser",
            "password": "test_password",
        })
        assert response.status_code == 302

        # generate
        response = client.get("/generate/config")
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        assert response.json == DTOOL_CONFIG


