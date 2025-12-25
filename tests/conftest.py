import asyncio
import pytest
from typing import AsyncGenerator

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from app.main import create_app
from app.db.base import Base
from app.api.deps import db_session_dep
from httpx import AsyncClient, ASGITransport
import uuid


# ---------- event loop (Windows-safe) ----------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------- test database ----------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    future=True,
)

TestSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def override_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


# ---------- app fixture ----------
@pytest.fixture(scope="session")
async def app() -> FastAPI:
    app = create_app()
    app.dependency_overrides[db_session_dep] = override_db_session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield app

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------- http client ----------
@pytest.fixture
async def client(app: FastAPI):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session

def user_payload():
    uid = uuid.uuid4().hex[:8]
    return {
        "email": f"user_{uid}@example.com",
        "username": f"user_{uid}",
        "password": "strongpassword123",
    }

@pytest.fixture
async def create_user(client):
    async def _create():
        payload = user_payload()
        res = await client.post("/api/v1/users", json=payload)
        assert res.status_code == 201
        return payload, res.json()["data"]
    return _create

@pytest.fixture
async def access_token(client, create_user):
    payload, _ = await create_user()

    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )
    assert login.status_code == 200

    return login.json()["data"]["access_token"]

@pytest.fixture
async def auth_header(access_token):
    return {"Authorization": f"Bearer {access_token}"}

from app.repositories.user_repository import UserRepository

@pytest.fixture
async def admin_auth_header(client, db_session):
    payload = user_payload()

    # register
    reg = await client.post("/api/v1/users", json=payload)
    user_id = reg.json()["data"]["id"]

    # promote to admin
    repo = UserRepository(db_session)
    user = await repo.get_by_id(user_id)
    user.is_admin = True
    await repo.update(user)

    # login
    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )

    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

