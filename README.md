# User Management Service (FastAPI)

A **production-ready, reusable User Management backend service** built with **FastAPI**, **async SQLAlchemy**, and **PostgreSQL**.

Designed to be plugged into multiple projects to handle **authentication, authorization, user lifecycle, and admin controls** with clean architecture and Docker support.

---

## ✨ Features

### Authentication & Security
- User registration
- Login with email & password
- JWT **access tokens**
- JWT **refresh tokens**
- Refresh token endpoint
- Password hashing using **bcrypt**
- Swagger UI **Authorize (Bearer token)** support

### User Management
- Get current user (`/users/me`)
- Update profile (username)
- Change password (with verification)
- Soft deactivate users (`is_active` flag)

### Admin Features
- Admin-only user listing
- Admin user deactivation
- Authorization via dependency (`is_admin` flag)
- RBAC-ready design

### Architecture & Infra
- Async SQLAlchemy 2.x
- Alembic migrations
- Clean layered architecture:
  - API → Services → Repositories → DB
- Domain-level errors (no HTTP logic in services)
- Uniform API response structure
- Dockerized API + PostgreSQL
- Migrations auto-run on container startup
- Windows / Linux / CI compatible

---

## 🗂 Project Structure
app/
├── api/
│   ├── deps.py
│   └── v1/
│       ├── auth.py
│       └── users.py
│
├── core/
│   ├── config.py
│   ├── logging.py
│   └── security.py
│
├── db/
│   ├── base.py
│   ├── session.py
│   └── migrations/
│
├── models/
│   ├── base.py
│   └── user.py
│
├── repositories/
│   └── user_repository.py
│
├── services/
│   ├── auth_service.py
│   ├── user_service.py
│   └── errors.py
│
├── schemas/
│   ├── auth.py
│   ├── user.py
│   └── common.py
│
├── exceptions/
│   └── handlers.py
│
├── main.py
│
entrypoint.sh
Dockerfile
docker-compose.yml
alembic.ini
pyproject.toml
uv.lock


---

## 🔁 API Response Format

All endpoints return a uniform response:

```json
{
  "success": true,
  "data": {},
  "error": null
}

{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}

🚀 Setup & Run (Docker Recommended)
Prerequisites

Docker Desktop

Docker Compose