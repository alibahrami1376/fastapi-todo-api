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


def test_login_inactive_user(client, db, login_payload):

    from models import UserModel

    inactive_user = UserModel(
        email="inactive@test.com",
        username=UserModel.generate_random_username(),
        is_active=False,
    )
    inactive_user.set_password("Aa@123456")
    db.add(inactive_user)
    db.flush()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@test.com", "password": "Aa@123456"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


def test_login_deleted_user(client, db):
    from datetime import datetime, timezone

    from models import UserModel

    deleted_user = UserModel(
        email="deleted@test.com",
        username=UserModel.generate_random_username(),
        is_active=True,
    )
    deleted_user.set_password("Aa@123456")
    deleted_user.deleted_at = datetime.now(timezone.utc)
    db.add(deleted_user)
    db.flush()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "deleted@test.com", "password": "Aa@123456"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BAD_REQUEST"


# ---------------------------------------------------------
# Refresh token
# ---------------------------------------------------------


def test_refresh_success(client, login_tokens):
    """Same IP + User-Agent as login → tokens refreshed."""
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {login_tokens['refresh_token']}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"
    assert data["refresh_token"] != login_tokens["refresh_token"]


def test_refresh_token_is_rotated(client, login_tokens):
    """Old refresh token must be invalid after rotation."""
    old_refresh = login_tokens["refresh_token"]

    client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {old_refresh}"},
    )

    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {old_refresh}"},
    )

    assert response.status_code == 401


def test_refresh_with_access_token_fails(client, login_tokens):
    """Passing the access token to /refresh must fail (wrong type)."""
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {login_tokens['access_token']}"},
    )

    assert response.status_code == 401


def test_refresh_invalid_token(client, user):
    """Garbage token → 401."""
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": "Bearer not.a.valid.token"},
    )

    assert response.status_code == 401


def test_refresh_missing_token(client, user):
    """No Authorization header → 401 (HTTPBearer auto_error=False path)."""
    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


# ---------------------------------------------------------
# Fingerprint — cross-client spoofing
# ---------------------------------------------------------


def test_refresh_fingerprint_mismatch(client, user):
    """
    Login from one User-Agent, then try to refresh from a different one.
    The fingerprint stored in the session must not match → 401.
    """
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "Aa@123456"},
        headers={"User-Agent": "LegitBrowser/1.0"},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    spoof_response = client.post(
        "/api/v1/auth/refresh",
        headers={
            "Authorization": f"Bearer {refresh_token}",
            "User-Agent": "EvilBot/9.9",
        },
    )

    assert spoof_response.status_code == 401
    data = spoof_response.json()
    assert data["success"] is False


def test_refresh_fingerprint_match(client, user):
    """
    Login and refresh with the same User-Agent → must succeed.
    """
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": "Aa@123456"},
        headers={"User-Agent": "LegitBrowser/1.0"},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        headers={
            "Authorization": f"Bearer {refresh_token}",
            "User-Agent": "LegitBrowser/1.0",
        },
    )

    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert data["access_token"]
    assert data["refresh_token"]
