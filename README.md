# User Management Service

Production-ready FastAPI-based user management and authentication service designed for reuse across multiple backend projects.

## Features
## Architecture
## Authentication Flows
## API Overview
## Tech Stack
## Running Locally
## Running Tests
## Design Decisions
## Future Improvements

# User Management Service
This repository contains a reusable user management and authentication service built with FastAPI.

It is designed as a standalone backend service that can be plugged into multiple projects requiring authentication, authorization, and user lifecycle management.

## Features

- User registration and login
- JWT-based authentication (access + refresh tokens)
- Stateful refresh token handling
- Secure logout with token revocation
- Password reset (forgot/reset flow with one-time tokens)
- Role-based access control (admin vs user)
- Async SQLAlchemy with Alembic migrations
- Dockerized development setup
- Integration tests with pytest
- CI via GitHub Actions

## Architecture

The service follows a layered architecture:

- **API layer**: FastAPI routers (request/response handling)
- **Service layer**: Business logic and orchestration
- **Repository layer**: Database access and persistence
- **Models**: SQLAlchemy ORM models
- **Schemas**: Pydantic request/response models

Each layer has a single responsibility, making the system easy to test and extend.

## Authentication Flows

### Login
1. User submits credentials
2. Server issues access + refresh tokens
3. Refresh token is hashed and persisted in the database

### Refresh Token
1. Client sends refresh token
2. Token is validated against the database
3. New access token is issued

### Logout
1. Client sends refresh token
2. Token is revoked in the database
3. Further refresh attempts fail

### Password Reset
1. User requests password reset
2. One-time reset token is generated and stored (hashed)
3. User resets password using token
4. All active sessions are invalidated

## API Overview

- POST /users — register user
- POST /auth/login — login
- POST /auth/refresh — refresh access token
- POST /auth/logout — logout
- POST /auth/forgot-password — initiate password reset
- POST /auth/reset-password — reset password
- GET /users/me — current user
- GET /admin/users — admin-only user listing

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy (async)
- Alembic
- PostgreSQL
- JWT
- pytest
- Docker & Docker Compose
- GitHub Actions

## Running Locally
docker compose up --build

## API will be available at:
http://localhost:8000/docs

## Running Tests
pytest -q

# Tests include integration coverage for:

- authentication

- authorization

- password reset

- admin access


---

## Design Decisions

- Refresh tokens are stored hashed for security
- Logout revokes refresh tokens instead of blacklisting access tokens
- Password reset tokens are one-time use and expire
- Services own database sessions to manage transactions
- Tests use real API calls instead of mocking internals

## Future Improvements

- Email delivery for password reset and verification
- Refresh token rotation
- Rate limiting on auth endpoints
- Account lockout on repeated failed logins
- OAuth provider support
