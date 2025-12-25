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
