# User Registration & Search API Design

## Overview

FastAPI application for user registration and search, using DynamoDB (Local via Docker) as the data store and uv for project management.

## Tech Stack

- **Framework**: FastAPI
- **Package Manager**: uv
- **Database**: DynamoDB Local (Docker)
- **AWS SDK**: boto3
- **Validation**: Pydantic v2

## Project Structure

```
fastapi-sandox/
├── pyproject.toml
├── docker-compose.yml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── db.py
│   └── routers/
│       ├── __init__.py
│       └── users.py
└── tests/
    ├── __init__.py
    └── test_users.py
```

## DynamoDB Table Design

**Table**: `users`

| Attribute  | Type       | Role                        |
|-----------|------------|-----------------------------|
| user_id   | S (UUID)   | Partition Key               |
| name      | S          | GSI "name-index" PK        |
| email     | S          | GSI "email-index" PK       |
| age       | N          | Attribute                   |
| address   | S          | Attribute                   |
| created_at| S (ISO8601)| Attribute                   |

**Global Secondary Indexes**:
- `name-index`: PK=name - query users by name
- `email-index`: PK=email - query users by email

## API Endpoints

| Method | Path               | Description              |
|--------|--------------------|--------------------------|
| POST   | `/users`           | Register a new user      |
| GET    | `/users/{user_id}` | Get user by ID           |
| GET    | `/users/search`    | Search by name/email     |
| GET    | `/users`           | List all users (Scan)    |

## Search Logic

- `name` param → Query `name-index` GSI
- `email` param → Query `email-index` GSI
- Both params → Query one GSI, filter results
- No params → Scan (full table scan)

## Infrastructure

- DynamoDB Local runs via `docker-compose.yml`
- Table and GSIs created on app startup via `db.py`
- Endpoint configurable via `config.py` (default: `http://localhost:8000`)
