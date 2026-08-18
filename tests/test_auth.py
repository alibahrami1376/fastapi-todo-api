# test_register_success
def test_register_success(client, register_payload):

    response = client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] > 0
    assert data["detail"] == "Your account has been created successfully."
    assert data["email"] == register_payload["email"]


def test_register_duplicate_email(client, user, register_payload):

    response = client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )
    data = response.json()
    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"]["code"] == "BAD_REQUEST"
    assert data["error"]["message"] == "An account with this email already exists."


def test_login_success(client, user, login_payload):

    response = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    data = response.json()
    assert response.status_code == 200
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, user, invalid_login_payload):

    response = client.post(
        "/api/v1/auth/login",
        json=invalid_login_payload,
    )

    data = response.json()
    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"]["code"] == "BAD_REQUEST"
    assert data["error"]["message"] == "Invalid email or password."


def test_register_password_mismatch(client, register_payload):
    register_payload["confirm_password"] = "Bb@123456"

    response = client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )

    data = response.json()

    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"]["code"] == "BAD_REQUEST"


def test_register_invalid_email(client, register_payload):
    register_payload["email"] = "invalid-email"

    response = client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )

    data = response.json()

    assert response.status_code == 422
    assert data["success"] is False


def test_login_nonexistent_email(client, login_payload):
    login_payload["email"] = "notfound@test.com"

    response = client.post(
        "/api/v1/auth/login",
        json=login_payload,
    )

    data = response.json()

    assert response.status_code == 400
    assert data["success"] is False
    assert data["error"]["code"] == "BAD_REQUEST"
    assert data["error"]["message"] == "Invalid email or password."


def test_login_missing_field(client):
    payload = {
        "password": "Aa@123456",
    }

    response = client.post(
        "/api/v1/auth/login",
        json=payload,
    )

    assert response.status_code == 422
