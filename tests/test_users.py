import pytest


@pytest.mark.asyncio
async def test_user_registration(client, create_user):
    payload, data = await create_user()

    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_current_user_me(client, auth_header):
    response = await client.get(
        "/api/v1/users/me",
        headers=auth_header,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["error"] is None

    data = body["data"]
    assert "email" in data
    assert "username" in data
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_without_token_fails(client):
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
