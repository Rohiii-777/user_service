import pytest


@pytest.mark.asyncio
async def test_non_admin_cannot_list_users(client, auth_header):
    response = await client.get(
        "/api/v1/admin/users",
        headers=auth_header,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_users(client, admin_auth_header):
    response = await client.get(
        "/api/v1/admin/users",
        headers=admin_auth_header,
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) >= 1
