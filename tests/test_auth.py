import pytest


@pytest.mark.asyncio
async def test_login_returns_tokens(client, create_user):
    payload, _ = await create_user()

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["error"] is None

    data = body["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_refresh_token_returns_new_access_token(client, create_user):
    payload, _ = await create_user()

    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    tokens = login.json()["data"]

    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert refresh.status_code == 200

    new_access_token = refresh.json()["data"]["access_token"]
    assert new_access_token
    assert new_access_token != tokens["access_token"]

@pytest.mark.asyncio
async def test_refresh_token_cannot_access_protected_route(client, create_user):
    payload, _ = await create_user()

    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    refresh_token = login.json()["data"]["refresh_token"]

    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client, create_user):
    payload, _ = await create_user()

    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    refresh_token = login.json()["data"]["refresh_token"]

    # logout
    logout = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
    )
    assert logout.status_code == 200

    # refresh should now fail
    refresh = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh.status_code == 401

@pytest.mark.asyncio
async def test_forgot_password_returns_reset_token(client, create_user):
    payload, _ = await create_user()

    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": payload["email"]},
    )

    assert response.status_code == 200
    token = response.json()["data"]["reset_token"]
    assert token is not None

@pytest.mark.asyncio
async def test_forgot_password_unknown_email_still_succeeds(client):
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "doesnotexist@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_reset_password_success(client, create_user):
    payload, _ = await create_user()

    # forgot password
    forgot = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": payload["email"]},
    )
    reset_token = forgot.json()["data"]["reset_token"]

    # reset password
    response = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": "newstrongpassword123",
        },
    )

    assert response.status_code == 200

    # login with new password
    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": "newstrongpassword123",
        },
    )

    assert login.status_code == 200

@pytest.mark.asyncio
async def test_reset_password_token_cannot_be_reused(client, create_user):
    payload, _ = await create_user()

    forgot = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": payload["email"]},
    )
    reset_token = forgot.json()["data"]["reset_token"]

    # first reset
    await client.post(
        "/api/v1/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": "newstrongpassword123",
        },
    )

    # reuse token
    second = await client.post(
        "/api/v1/auth/reset-password",
        json={
            "reset_token": reset_token,
            "new_password": "anotherpassword123",
        },
    )

    assert second.status_code == 401
