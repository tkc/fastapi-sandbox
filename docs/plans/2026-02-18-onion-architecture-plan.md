# Onion Architecture Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the flat FastAPI User API into an onion architecture with domain/usecase/infrastructure layers, dependency-injector DI, and unit tests.

**Architecture:** Onion architecture with 4 layers (presentation, usecase, domain, infrastructure). Domain layer defines repository interfaces; infrastructure implements them. dependency-injector wires everything together. Existing integration tests must pass after refactoring.

**Tech Stack:** FastAPI, Pydantic v2, dependency-injector, boto3 (DynamoDB), pytest

---

### Task 1: Add dependency-injector

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add dependency-injector to dependencies**

Add `dependency-injector` to the project:

```bash
cd /Users/tkc/github/fastapi-sandox && uv add dependency-injector
```

**Step 2: Verify install**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run python -c "from dependency_injector import containers; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add dependency-injector"
```

---

### Task 2: Create domain layer - User entity

**Files:**
- Create: `app/domain/__init__.py`
- Create: `app/domain/user/__init__.py`
- Create: `app/domain/user/entity.py`
- Test: `tests/domain/__init__.py`
- Test: `tests/domain/test_user_entity.py`

**Step 1: Create directory structure and `__init__.py` files**

Create empty `__init__.py` files:

- `app/domain/__init__.py`
- `app/domain/user/__init__.py`
- `tests/domain/__init__.py`

**Step 2: Write the failing test**

`tests/domain/test_user_entity.py`:

```python
from app.domain.user.entity import User


def test_create_generates_user_id():
    user = User.create(
        name="Taro",
        email="taro@example.com",
        age=30,
        address="Tokyo",
    )
    assert user.user_id is not None
    assert len(user.user_id) == 36  # UUID format


def test_create_generates_created_at():
    user = User.create(
        name="Taro",
        email="taro@example.com",
        age=30,
        address="Tokyo",
    )
    assert user.created_at is not None
    assert "T" in user.created_at  # ISO8601 format


def test_create_preserves_fields():
    user = User.create(
        name="Hanako",
        email="hanako@example.com",
        age=25,
        address="Osaka",
    )
    assert user.name == "Hanako"
    assert user.email == "hanako@example.com"
    assert user.age == 25
    assert user.address == "Osaka"
```

**Step 3: Run test to verify it fails**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run pytest tests/domain/test_user_entity.py -v
```

Expected: FAIL with `ModuleNotFoundError` or `ImportError`

**Step 4: Write minimal implementation**

`app/domain/user/entity.py`:

```python
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    name: str
    email: str
    age: int
    address: str
    created_at: str

    @classmethod
    def create(
        cls,
        name: str,
        email: str,
        age: int,
        address: str,
    ) -> "User":
        return cls(
            user_id=str(uuid.uuid4()),
            name=name,
            email=email,
            age=age,
            address=address,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
```

**Step 5: Run test to verify it passes**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run pytest tests/domain/test_user_entity.py -v
```

Expected: 3 passed

**Step 6: Commit**

```bash
git add app/domain/ tests/domain/
git commit -m "feat: add User entity with factory method in domain layer"
```

---

### Task 3: Create domain layer - Repository interface

**Files:**
- Create: `app/domain/user/i_user_repository.py`

**Step 1: Write the repository interface**

`app/domain/user/i_user_repository.py`:

```python
from abc import ABC, abstractmethod

from app.domain.user.entity import User


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, user_id: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def search_by_name(self, name: str) -> list[User]:
        raise NotImplementedError

    @abstractmethod
    def search_by_email(self, email: str) -> list[User]:
        raise NotImplementedError
```

**Step 2: Verify import works**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run python -c "from app.domain.user.i_user_repository import IUserRepository; print('OK')"
```

Expected: `OK`

**Step 3: Commit**

```bash
git add app/domain/user/i_user_repository.py
git commit -m "feat: add IUserRepository interface in domain layer"
```

---

### Task 4: Create core layer - Config and exceptions

**Files:**
- Create: `app/core/__init__.py`
- Create: `app/core/config.py` (move from `app/config.py`)
- Create: `app/core/exceptions.py`

**Step 1: Create core directory and move config**

Create `app/core/__init__.py` (empty).

`app/core/config.py` — copy contents from existing `app/config.py`:

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dynamodb_endpoint: str = "http://localhost:8000"
    dynamodb_region: str = "us-east-1"
    dynamodb_table_name: str = "users"


settings = Settings()
```

**Step 2: Create custom exceptions**

`app/core/exceptions.py`:

```python
class UserNotFoundError(Exception):
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")
```

**Step 3: Verify imports**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run python -c "from app.core.config import settings; from app.core.exceptions import UserNotFoundError; print('OK')"
```

Expected: `OK`

**Step 4: Commit**

```bash
git add app/core/
git commit -m "feat: add core layer with config and exceptions"
```

---

### Task 5: Create infrastructure layer - Datasource

**Files:**
- Create: `app/infrastructure/__init__.py`
- Create: `app/infrastructure/datasource/__init__.py`
- Create: `app/infrastructure/datasource/dynamodb.py` (move from `app/db.py`)

**Step 1: Create directory structure**

Create empty `__init__.py` files:

- `app/infrastructure/__init__.py`
- `app/infrastructure/datasource/__init__.py`

**Step 2: Write datasource module**

`app/infrastructure/datasource/dynamodb.py` — move and update from `app/db.py`:

```python
import boto3

from app.core.config import settings


def get_dynamodb_resource():
    return boto3.resource(
        "dynamodb",
        endpoint_url=settings.dynamodb_endpoint,
        region_name=settings.dynamodb_region,
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )


def get_table():
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.dynamodb_table_name)


def create_users_table():
    dynamodb = get_dynamodb_resource()
    existing_tables = dynamodb.meta.client.list_tables()["TableNames"]
    if settings.dynamodb_table_name in existing_tables:
        return dynamodb.Table(settings.dynamodb_table_name)

    table = dynamodb.create_table(
        TableName=settings.dynamodb_table_name,
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "name", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "name-index",
                "KeySchema": [
                    {"AttributeName": "name", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            },
            {
                "IndexName": "email-index",
                "KeySchema": [
                    {"AttributeName": "email", "KeyType": "HASH"},
                ],
                "Projection": {"ProjectionType": "ALL"},
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5,
                },
            },
        ],
        BillingMode="PROVISIONED",
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
    )
    table.wait_until_exists()
    return table
```

**Step 3: Verify import**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run python -c "from app.infrastructure.datasource.dynamodb import get_table, create_users_table; print('OK')"
```

Expected: `OK`

**Step 4: Commit**

```bash
git add app/infrastructure/
git commit -m "feat: add infrastructure datasource layer with DynamoDB"
```

---

### Task 6: Create infrastructure layer - Repository implementation

**Files:**
- Create: `app/infrastructure/repository/__init__.py`
- Create: `app/infrastructure/repository/user_dynamodb_repository.py`

**Step 1: Create directory**

Create empty `app/infrastructure/repository/__init__.py`.

**Step 2: Write repository implementation**

`app/infrastructure/repository/user_dynamodb_repository.py`:

```python
from boto3.dynamodb.conditions import Key

from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository


class UserDynamoDBRepository(IUserRepository):
    def __init__(self, table) -> None:
        self._table = table

    def save(self, user: User) -> None:
        self._table.put_item(Item=user.model_dump())

    def find_by_id(self, user_id: str) -> User | None:
        response = self._table.get_item(Key={"user_id": user_id})
        item = response.get("Item")
        if not item:
            return None
        return User(**item)

    def find_all(self) -> list[User]:
        response = self._table.scan()
        return [User(**item) for item in response["Items"]]

    def search_by_name(self, name: str) -> list[User]:
        response = self._table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(name),
        )
        return [User(**item) for item in response["Items"]]

    def search_by_email(self, email: str) -> list[User]:
        response = self._table.query(
            IndexName="email-index",
            KeyConditionExpression=Key("email").eq(email),
        )
        return [User(**item) for item in response["Items"]]
```

**Step 3: Verify import**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run python -c "from app.infrastructure.repository.user_dynamodb_repository import UserDynamoDBRepository; print('OK')"
```

Expected: `OK`

**Step 4: Commit**

```bash
git add app/infrastructure/repository/
git commit -m "feat: add UserDynamoDBRepository implementing IUserRepository"
```

---

### Task 7: Create schema layer

**Files:**
- Create: `app/schemas/__init__.py`
- Create: `app/schemas/user.py` (move and extend from `app/models.py`)

**Step 1: Create directory**

Create empty `app/schemas/__init__.py`.

**Step 2: Write schemas**

`app/schemas/user.py`:

```python
from pydantic import BaseModel, EmailStr, Field

from app.domain.user.entity import User


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    address: str = Field(..., min_length=1, max_length=500)


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    age: int
    address: str
    created_at: str

    @classmethod
    def from_entity(cls, user: User) -> "UserResponse":
        return cls(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            age=user.age,
            address=user.address,
            created_at=user.created_at,
        )


class UserSearchQuery(BaseModel):
    name: str | None = None
    email: str | None = None
```

**Step 3: Verify import**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run python -c "from app.schemas.user import UserCreate, UserResponse, UserSearchQuery; print('OK')"
```

Expected: `OK`

**Step 4: Commit**

```bash
git add app/schemas/
git commit -m "feat: add schema layer with user DTOs"
```

---

### Task 8: Create usecase layer

**Files:**
- Create: `app/usecase/__init__.py`
- Create: `app/usecase/user/__init__.py`
- Create: `app/usecase/user/create_user_usecase.py`
- Create: `app/usecase/user/get_user_usecase.py`
- Create: `app/usecase/user/list_users_usecase.py`
- Create: `app/usecase/user/search_users_usecase.py`
- Test: `tests/usecase/__init__.py`
- Test: `tests/usecase/test_user_usecases.py`

**Step 1: Create directory structure**

Create empty `__init__.py` files:

- `app/usecase/__init__.py`
- `app/usecase/user/__init__.py`
- `tests/usecase/__init__.py`

**Step 2: Write the failing tests**

`tests/usecase/test_user_usecases.py`:

```python
from unittest.mock import MagicMock

from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserCreate
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase


def _make_user(**overrides) -> User:
    defaults = {
        "user_id": "test-uuid",
        "name": "Taro",
        "email": "taro@example.com",
        "age": 30,
        "address": "Tokyo",
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    defaults.update(overrides)
    return User(**defaults)


class TestCreateUserUseCase:
    def test_creates_and_saves_user(self):
        repo = MagicMock(spec=IUserRepository)
        usecase = CreateUserUseCase(user_repository=repo)

        result = usecase.execute(
            UserCreate(name="Taro", email="taro@example.com", age=30, address="Tokyo")
        )

        repo.save.assert_called_once()
        saved_user = repo.save.call_args[0][0]
        assert saved_user.name == "Taro"
        assert saved_user.email == "taro@example.com"
        assert result.name == "Taro"
        assert result.user_id is not None


class TestGetUserUseCase:
    def test_returns_user_when_found(self):
        repo = MagicMock(spec=IUserRepository)
        user = _make_user()
        repo.find_by_id.return_value = user
        usecase = GetUserUseCase(user_repository=repo)

        result = usecase.execute("test-uuid")

        assert result.user_id == "test-uuid"
        assert result.name == "Taro"

    def test_raises_when_not_found(self):
        repo = MagicMock(spec=IUserRepository)
        repo.find_by_id.return_value = None
        usecase = GetUserUseCase(user_repository=repo)

        import pytest
        with pytest.raises(Exception):
            usecase.execute("nonexistent")


class TestListUsersUseCase:
    def test_returns_all_users(self):
        repo = MagicMock(spec=IUserRepository)
        repo.find_all.return_value = [_make_user(), _make_user(name="Hanako")]
        usecase = ListUsersUseCase(user_repository=repo)

        result = usecase.execute()

        assert len(result) == 2


class TestSearchUsersUseCase:
    def test_search_by_name(self):
        repo = MagicMock(spec=IUserRepository)
        repo.search_by_name.return_value = [_make_user()]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name="Taro", email=None)

        assert len(result) == 1
        repo.search_by_name.assert_called_once_with("Taro")

    def test_search_by_email(self):
        repo = MagicMock(spec=IUserRepository)
        repo.search_by_email.return_value = [_make_user()]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name=None, email="taro@example.com")

        assert len(result) == 1
        repo.search_by_email.assert_called_once_with("taro@example.com")

    def test_search_by_name_and_email(self):
        repo = MagicMock(spec=IUserRepository)
        repo.search_by_name.return_value = [
            _make_user(),
            _make_user(email="other@example.com"),
        ]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name="Taro", email="taro@example.com")

        assert len(result) == 1
        assert result[0].email == "taro@example.com"

    def test_search_no_params_returns_all(self):
        repo = MagicMock(spec=IUserRepository)
        repo.find_all.return_value = [_make_user()]
        usecase = SearchUsersUseCase(user_repository=repo)

        result = usecase.execute(name=None, email=None)

        assert len(result) == 1
        repo.find_all.assert_called_once()
```

**Step 3: Run tests to verify they fail**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run pytest tests/usecase/test_user_usecases.py -v
```

Expected: FAIL with `ModuleNotFoundError`

**Step 4: Write usecase implementations**

`app/usecase/user/create_user_usecase.py`:

```python
from app.domain.user.entity import User
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserCreate, UserResponse


class CreateUserUseCase:
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, user_create: UserCreate) -> UserResponse:
        user = User.create(
            name=user_create.name,
            email=user_create.email,
            age=user_create.age,
            address=user_create.address,
        )
        self._user_repository.save(user)
        return UserResponse.from_entity(user)
```

`app/usecase/user/get_user_usecase.py`:

```python
from app.core.exceptions import UserNotFoundError
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserResponse


class GetUserUseCase:
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(self, user_id: str) -> UserResponse:
        user = self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return UserResponse.from_entity(user)
```

`app/usecase/user/list_users_usecase.py`:

```python
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserResponse


class ListUsersUseCase:
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(self) -> list[UserResponse]:
        users = self._user_repository.find_all()
        return [UserResponse.from_entity(user) for user in users]
```

`app/usecase/user/search_users_usecase.py`:

```python
from app.domain.user.i_user_repository import IUserRepository
from app.schemas.user import UserResponse


class SearchUsersUseCase:
    def __init__(self, user_repository: IUserRepository) -> None:
        self._user_repository = user_repository

    def execute(
        self, name: str | None, email: str | None
    ) -> list[UserResponse]:
        if name and email:
            users = self._user_repository.search_by_name(name)
            users = [u for u in users if u.email == email]
        elif name:
            users = self._user_repository.search_by_name(name)
        elif email:
            users = self._user_repository.search_by_email(email)
        else:
            users = self._user_repository.find_all()
        return [UserResponse.from_entity(user) for user in users]
```

**Step 5: Run tests to verify they pass**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run pytest tests/usecase/test_user_usecases.py -v
```

Expected: 8 passed

**Step 6: Commit**

```bash
git add app/usecase/ tests/usecase/
git commit -m "feat: add usecase layer with unit tests"
```

---

### Task 9: Create DI container

**Files:**
- Create: `app/container/__init__.py`
- Create: `app/container/container.py`

**Step 1: Create directory**

Create empty `app/container/__init__.py`.

**Step 2: Write container**

`app/container/container.py`:

```python
from dependency_injector import containers, providers

from app.infrastructure.datasource.dynamodb import get_table
from app.infrastructure.repository.user_dynamodb_repository import (
    UserDynamoDBRepository,
)
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["app.api.v1.endpoints.users"],
    )

    dynamodb_table = providers.Singleton(get_table)

    user_repository = providers.Singleton(
        UserDynamoDBRepository,
        table=dynamodb_table,
    )

    create_user_usecase = providers.Factory(
        CreateUserUseCase,
        user_repository=user_repository,
    )

    get_user_usecase = providers.Factory(
        GetUserUseCase,
        user_repository=user_repository,
    )

    list_users_usecase = providers.Factory(
        ListUsersUseCase,
        user_repository=user_repository,
    )

    search_users_usecase = providers.Factory(
        SearchUsersUseCase,
        user_repository=user_repository,
    )
```

**Step 3: Commit**

```bash
git add app/container/
git commit -m "feat: add DI container with dependency-injector"
```

---

### Task 10: Create presentation layer

**Files:**
- Create: `app/api/__init__.py`
- Create: `app/api/v1/__init__.py`
- Create: `app/api/v1/router.py`
- Create: `app/api/v1/endpoints/__init__.py`
- Create: `app/api/v1/endpoints/users.py`

**Step 1: Create directory structure**

Create empty `__init__.py` files:

- `app/api/__init__.py`
- `app/api/v1/__init__.py`
- `app/api/v1/endpoints/__init__.py`

**Step 2: Write endpoints**

`app/api/v1/endpoints/users.py`:

```python
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query

from app.container.container import Container
from app.core.exceptions import UserNotFoundError
from app.schemas.user import UserCreate, UserResponse
from app.usecase.user.create_user_usecase import CreateUserUseCase
from app.usecase.user.get_user_usecase import GetUserUseCase
from app.usecase.user.list_users_usecase import ListUsersUseCase
from app.usecase.user.search_users_usecase import SearchUsersUseCase

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=201)
@inject
def create_user(
    user: UserCreate,
    usecase: CreateUserUseCase = Depends(Provide[Container.create_user_usecase]),
):
    return usecase.execute(user)


@router.get("/search", response_model=list[UserResponse])
@inject
def search_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    usecase: SearchUsersUseCase = Depends(Provide[Container.search_users_usecase]),
):
    return usecase.execute(name=name, email=email)


@router.get("/{user_id}", response_model=UserResponse)
@inject
def get_user(
    user_id: str,
    usecase: GetUserUseCase = Depends(Provide[Container.get_user_usecase]),
):
    try:
        return usecase.execute(user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("", response_model=list[UserResponse])
@inject
def list_users(
    usecase: ListUsersUseCase = Depends(Provide[Container.list_users_usecase]),
):
    return usecase.execute()
```

**Step 3: Write router aggregation**

`app/api/v1/router.py`:

```python
from fastapi import APIRouter

from app.api.v1.endpoints import users

v1_router = APIRouter()
v1_router.include_router(users.router, prefix="/users", tags=["users"])
```

**Step 4: Commit**

```bash
git add app/api/
git commit -m "feat: add presentation layer with v1 endpoints"
```

---

### Task 11: Update main.py and wire everything

**Files:**
- Modify: `app/main.py`

**Step 1: Rewrite main.py**

`app/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import v1_router
from app.container.container import Container
from app.infrastructure.datasource.dynamodb import create_users_table


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_users_table()
    yield


def create_app() -> FastAPI:
    container = Container()
    app = FastAPI(title="User API", lifespan=lifespan)
    app.container = container
    app.include_router(v1_router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
```

**Step 2: Commit**

```bash
git add app/main.py
git commit -m "refactor: update main.py to wire DI container and new router"
```

---

### Task 12: Update integration tests and conftest

**Files:**
- Modify: `tests/conftest.py`
- Modify: `tests/test_users.py`

**Step 1: Update conftest.py**

`tests/conftest.py`:

```python
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.infrastructure.datasource.dynamodb import (
    create_users_table,
    get_dynamodb_resource,
)
from app.main import app


@pytest.fixture(autouse=True)
def setup_and_teardown_table():
    """Create table before each test, delete after."""
    create_users_table()
    yield
    dynamodb = get_dynamodb_resource()
    table = dynamodb.Table(settings.dynamodb_table_name)
    table.delete()


@pytest.fixture
def client():
    return TestClient(app)
```

**Step 2: Run all tests**

`tests/test_users.py` requires no changes — the API contract (paths, request/response shapes) is unchanged.

```bash
cd /Users/tkc/github/fastapi-sandox && uv run pytest tests/ -v
```

Expected: All tests pass (integration tests + domain unit tests + usecase unit tests)

**Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "refactor: update conftest to use new import paths"
```

---

### Task 13: Remove old files

**Files:**
- Delete: `app/config.py`
- Delete: `app/db.py`
- Delete: `app/models.py`
- Delete: `app/routers/users.py`
- Delete: `app/routers/__init__.py`

**Step 1: Remove old files**

```bash
cd /Users/tkc/github/fastapi-sandox && rm app/config.py app/db.py app/models.py app/routers/users.py app/routers/__init__.py && rmdir app/routers
```

**Step 2: Run all tests to confirm nothing broke**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run pytest tests/ -v
```

Expected: All tests pass

**Step 3: Commit**

```bash
git add -A
git commit -m "refactor: remove old flat module files"
```

---

### Task 14: Final verification

**Step 1: Run full test suite**

```bash
cd /Users/tkc/github/fastapi-sandox && uv run pytest tests/ -v
```

Expected: All tests pass

**Step 2: Verify app starts**

```bash
cd /Users/tkc/github/fastapi-sandox && timeout 5 uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 || true
```

Expected: Application starts without import errors (will timeout after 5s, that's OK)

**Step 3: Final commit if any remaining changes**

```bash
git status
```
