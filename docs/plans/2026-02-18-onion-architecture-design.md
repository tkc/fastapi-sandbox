# Onion Architecture Refactoring Design

## Overview

Refactor the current flat FastAPI project structure into an onion architecture, following the RAKSUL TechBlog article pattern. Uses `dependency-injector` for DI and Pydantic BaseModel for domain entities.

## Directory Structure

```
app/
├── main.py
├── api/
│   └── v1/
│       ├── router.py
│       └── endpoints/
│           └── users.py
├── schemas/
│   └── user.py
├── usecase/
│   └── user/
│       ├── create_user_usecase.py
│       ├── get_user_usecase.py
│       ├── list_users_usecase.py
│       └── search_users_usecase.py
├── domain/
│   └── user/
│       ├── entity.py
│       └── i_user_repository.py
├── infrastructure/
│   ├── datasource/
│   │   └── dynamodb.py
│   └── repository/
│       └── user_dynamodb_repository.py
├── container/
│   └── container.py
└── core/
    ├── config.py
    └── exceptions.py
tests/
├── conftest.py
├── test_users.py
├── domain/
│   └── test_user_entity.py
└── usecase/
    └── test_user_usecases.py
```

## Layer Responsibilities

| Layer | Directory | Responsibility |
|---|---|---|
| Presentation | `api/v1/` | HTTP request/response bridging |
| Schema | `schemas/` | DTOs between api and usecase, validation |
| Use Case | `usecase/` | Orchestrate domain methods into use cases |
| Domain | `domain/` | Entities, repository interfaces |
| Infrastructure | `infrastructure/` | Repository implementations, DynamoDB connection |
| DI | `container/` | dependency-injector bindings |
| Core | `core/` | Config, exceptions |

## Domain Layer

### User Entity (`domain/user/entity.py`)

- Pydantic BaseModel base
- Fields: user_id, name, email, age, address, created_at
- Factory method `create()` for UUID generation and timestamp creation

### Repository Interface (`domain/user/i_user_repository.py`)

```python
class IUserRepository(ABC):
    def save(self, user: User) -> None: ...
    def find_by_id(self, user_id: str) -> User | None: ...
    def find_all(self) -> list[User]: ...
    def search_by_name(self, name: str) -> list[User]: ...
    def search_by_email(self, email: str) -> list[User]: ...
```

DIP: Domain layer defines the interface, infrastructure layer implements it.

## Infrastructure Layer

### DynamoDB Datasource (`infrastructure/datasource/dynamodb.py`)

- Moved from current `db.py`
- `get_dynamodb_resource()` and `create_users_table()`

### Repository Implementation (`infrastructure/repository/user_dynamodb_repository.py`)

- Implements `IUserRepository`
- Receives DynamoDB table via constructor injection
- Consolidates all DynamoDB query logic currently in `routers/users.py`

## Use Case Layer

- One class per use case: CreateUser, GetUser, ListUsers, SearchUsers
- Receives `IUserRepository` via constructor
- Accepts schema DTOs, returns schema DTOs
- Calls domain entity factory methods and repository methods

## Schema Layer (`schemas/user.py`)

- `UserCreate`: Request validation (name length, email format, age range)
- `UserResponse`: Response structure with `from_entity()` class method
- `UserSearchQuery`: Search parameters

## Presentation Layer (`api/v1/`)

- Endpoints inject use cases via `Depends(Provide[Container.xxx_usecase])`
- Thin handlers: receive request, delegate to use case, return response
- `router.py` aggregates routers with `/users` prefix

## DI Container (`container/container.py`)

- `dependency-injector` DeclarativeContainer
- Binds `IUserRepository` -> `UserDynamoDBRepository`
- Provides Factory for each use case
- Wired to endpoint modules in `main.py`
- Test override via `container.user_repository.override()`

## Testing

- `tests/test_users.py`: Existing integration tests, updated imports
- `tests/domain/test_user_entity.py`: Unit tests for `User.create()`
- `tests/usecase/test_user_usecases.py`: Unit tests with mocked repository

## Dependencies

- Add `dependency-injector` to `pyproject.toml`
