# User Management Service (FastAPI)

A **production-ready, reusable user management backend** built with **FastAPI**, **async SQLAlchemy**, **JWT authentication**, and **PostgreSQL**.

Designed as a **standalone user service** that can be plugged into multiple applications with minimal changes.

---

## Why This Project Exists

Most side projects either:

* skip authentication entirely, or
* implement it in a fragile, hard-to-maintain way.

This service focuses on doing authentication **the right way**, with:

* clean architecture
* correct auth & authorization flows
* real-world backend patterns
* strong test coverage
* reusability across projects

The goal is not a demo — it’s a **baseline user service you can trust**.

---

## Architecture

The project follows a **layered architecture** with strict separation of concerns.

### Layers

* **API Layer**
  FastAPI routes. Handles HTTP concerns only (requests, responses, status codes).

* **Service Layer**
  Business logic, validation, orchestration.

* **Repository Layer**
  Database access using async SQLAlchemy.

* **Core**
  Security (JWT, password hashing), configuration, shared utilities.

* **DB**
  Async SQLAlchemy models and Alembic migrations.

### Design Principles

* No database logic in routes
* No HTTP logic in services
* Stateless authentication
* Explicit, testable boundaries between layers

---

## Authentication & Authorization

### Authentication Flow

1. User registers with email, username, and password
2. Passwords are securely hashed
3. Login returns:

   * **Access token (JWT)** — short-lived
   * **Refresh token (JWT)** — long-lived

---

### Access Tokens

* Used for protected endpoints

* Sent via header:

  ```http
  Authorization: Bearer <access_token>
  ```

* Short-lived by design

* Contains a unique token ID (`jti`) to ensure proper rotation

---

### Refresh Tokens

* Used **only** to obtain a new access token
* Cannot access protected routes
* Token type is explicitly enforced
* Access token rotation is guaranteed

---

### Admin Authorization

* Users have an `is_admin` flag
* Admin-only endpoints are protected via dependencies
* Non-admin access returns `403 Forbidden`

---

## API Overview

### Authentication

* `POST /api/v1/users` — Register
* `POST /api/v1/auth/login` — Login
* `POST /api/v1/auth/refresh` — Refresh access token

### User

* `GET /api/v1/users/me` — Get current user

### Admin

* `GET /api/v1/admin/users` — List users (admin only)

### API Docs

Swagger UI available at:

```
http://localhost:8000/docs
```

---

## Running Locally

### Requirements

* Docker
* Docker Compose

### Start the Service

```bash
docker compose up --build
```

### Services

* API → [http://localhost:8000](http://localhost:8000)
* Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
* PostgreSQL → internal Docker network

Database migrations run automatically on container startup.

---

## Testing

Tests are **async integration tests** using SQLite for speed and isolation.

```bash
pytest
```

### What’s Covered

* User registration
* Login & refresh token flow
* Protected routes
* Negative authentication cases
* Admin RBAC

Tests exercise the **real application stack**:

```
routes → services → repositories → database
```

---

## Tech Stack

* FastAPI
* SQLAlchemy (async)
* PostgreSQL
* Alembic
* JWT (access + refresh)
* Argon2 (password hashing)
* pytest + pytest-asyncio
* Docker & Docker Compose

---

## Design Decisions

* JWTs used instead of sessions for stateless authentication
* Service & repository layers keep routes thin
* SQLite used in tests for fast feedback
* Admin modeled as a simple flag for clarity and extensibility

---

## Reuse

This service can be reused by:

* pointing multiple applications to the same user service, or
* embedding it as a module inside a larger FastAPI system

---

## Status

This project is **feature-complete** for a baseline user management service.

Future enhancements (rate limiting, refresh token reuse detection, advanced RBAC, token revocation) can be added **without changing the core design**.
