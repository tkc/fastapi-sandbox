# User Registration & Search API Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a FastAPI application with user registration and search endpoints backed by DynamoDB Local.

**Architecture:** FastAPI app with a router-based structure. boto3 talks to DynamoDB Local (Docker). Table has GSIs for name/email search. Pydantic v2 for request/response validation.

**Tech Stack:** FastAPI, uv, boto3, Pydantic v2, DynamoDB Local (Docker), pytest, httpx

---

### Task 1: Initialize uv project and install dependencies

**Files:**
- Create: `pyproject.toml`

**Step 1: Initialize uv project**

Run:
```bash
cd /Users/tkc/github/fastapi-sandox
uv init
```

**Step 2: Add dependencies**

Run:
```bash
uv add fastapi uvicorn boto3
uv add --dev pytest httpx pytest-asyncio
```

**Step 3: Verify**

Run: `uv run python -c "import fastapi; print(fastapi.__version__)"`
Expected: Prints FastAPI version without error.

**Step 4: Commit**

```bash
git add pyproject.toml uv.lock .python-version
git commit -m "feat: initialize uv project with FastAPI and boto3 dependencies"
```

---

### Task 2: Create Docker Compose for DynamoDB Local

**Files:**
- Create: `docker-compose.yml`

**Step 1: Write docker-compose.yml**

```yaml
services:
  dynamodb-local:
    image: amazon/dynamodb-local:latest
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    command: "-jar DynamoDBLocal.jar -sharedDb -inMemory"
```

**Step 2: Start DynamoDB Local**

Run: `docker compose up -d`
Expected: Container starts successfully.

**Step 3: Verify DynamoDB Local is running**

Run: `aws dynamodb list-tables --endpoint-url http://localhost:8000 --region us-east-1 --no-cli-pager 2>/dev/null || curl -s http://localhost:8000`
Expected: Returns empty table list or healthy response.

**Step 4: Commit**

```bash
git add docker-compose.yml
git commit -m "infra: add docker-compose for DynamoDB Local"
```

---

### Task 3: Create config module

**Files:**
- Create: `app/__init__.py`
- Create: `app/config.py`

**Step 1: Create app package**

```python
# app/__init__.py
```
(empty file)

**Step 2: Write config.py**

```python
# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dynamodb_endpoint: str = "http://localhost:8000"
    dynamodb_region: str = "us-east-1"
    dynamodb_table_name: str = "users"


settings = Settings()
```

Note: This requires `pydantic-settings`. Add it:
```bash
uv add pydantic-settings
```

**Step 3: Verify**

Run: `uv run python -c "from app.config import settings; print(settings.dynamodb_endpoint)"`
Expected: `http://localhost:8000`

**Step 4: Commit**

```bash
git add app/__init__.py app/config.py pyproject.toml uv.lock
git commit -m "feat: add config module with DynamoDB settings"
```

---

### Task 4: Create DynamoDB client and table setup

**Files:**
- Create: `app/db.py`

**Step 1: Write db.py**

```python
# app/db.py
import boto3
from app.config import settings


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

**Step 2: Verify table creation (requires Docker running)**

Run: `uv run python -c "from app.db import create_users_table; t = create_users_table(); print(t.table_status)"`
Expected: `ACTIVE`

**Step 3: Commit**

```bash
git add app/db.py
git commit -m "feat: add DynamoDB client and table creation"
```

---

### Task 5: Create Pydantic models

**Files:**
- Create: `app/models.py`

**Step 1: Write models.py**

```python
# app/models.py
from pydantic import BaseModel, EmailStr, Field


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


class UserSearchQuery(BaseModel):
    name: str | None = None
    email: str | None = None
```

Note: `EmailStr` requires `email-validator`. Add it:
```bash
uv add email-validator
```

**Step 2: Verify**

Run: `uv run python -c "from app.models import UserCreate; u = UserCreate(name='test', email='a@b.com', age=25, address='Tokyo'); print(u)"`
Expected: Prints the model without error.

**Step 3: Commit**

```bash
git add app/models.py pyproject.toml uv.lock
git commit -m "feat: add Pydantic request/response models"
```

---

### Task 6: Create users router

**Files:**
- Create: `app/routers/__init__.py`
- Create: `app/routers/users.py`

**Step 1: Create routers package**

```python
# app/routers/__init__.py
```
(empty file)

**Step 2: Write users.py**

```python
# app/routers/users.py
import uuid
from datetime import datetime, timezone

from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, HTTPException, Query

from app.db import get_table
from app.models import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    table = get_table()
    user_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    item = {
        "user_id": user_id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "address": user.address,
        "created_at": created_at,
    }
    table.put_item(Item=item)
    return item


@router.get("/search", response_model=list[UserResponse])
def search_users(
    name: str | None = Query(default=None),
    email: str | None = Query(default=None),
):
    table = get_table()

    if name and email:
        response = table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(name),
        )
        items = [item for item in response["Items"] if item["email"] == email]
    elif name:
        response = table.query(
            IndexName="name-index",
            KeyConditionExpression=Key("name").eq(name),
        )
        items = response["Items"]
    elif email:
        response = table.query(
            IndexName="email-index",
            KeyConditionExpression=Key("email").eq(email),
        )
        items = response["Items"]
    else:
        response = table.scan()
        items = response["Items"]

    return items


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    table = get_table()
    response = table.get_item(Key={"user_id": user_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    return item


@router.get("", response_model=list[UserResponse])
def list_users():
    table = get_table()
    response = table.scan()
    return response["Items"]
```

**Step 3: Commit**

```bash
git add app/routers/__init__.py app/routers/users.py
git commit -m "feat: add users router with CRUD and search endpoints"
```

---

### Task 7: Create FastAPI main app with lifespan

**Files:**
- Create: `app/main.py`

**Step 1: Write main.py**

```python
# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_users_table
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_users_table()
    yield


app = FastAPI(title="User API", lifespan=lifespan)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 2: Verify app starts (requires Docker running)**

Run: `uv run uvicorn app.main:app --host 0.0.0.0 --port 8001` (use 8001 to avoid conflict with DynamoDB on 8000)
Expected: App starts without error. Visit `http://localhost:8001/docs` to see Swagger UI.

**Step 3: Commit**

```bash
git add app/main.py
git commit -m "feat: add FastAPI app with lifespan and router registration"
```

---

### Task 8: Write tests

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_users.py`

**Step 1: Create test package and conftest**

```python
# tests/__init__.py
```

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from app.db import create_users_table, get_dynamodb_resource
from app.config import settings
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

**Step 2: Write test_users.py**

```python
# tests/test_users.py


def test_create_user(client):
    response = client.post(
        "/users",
        json={
            "name": "Taro Yamada",
            "email": "taro@example.com",
            "age": 30,
            "address": "Tokyo",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Taro Yamada"
    assert data["email"] == "taro@example.com"
    assert "user_id" in data
    assert "created_at" in data


def test_get_user(client):
    create_resp = client.post(
        "/users",
        json={
            "name": "Hanako",
            "email": "hanako@example.com",
            "age": 25,
            "address": "Osaka",
        },
    )
    user_id = create_resp.json()["user_id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Hanako"


def test_get_user_not_found(client):
    response = client.get("/users/nonexistent-id")
    assert response.status_code == 404


def test_list_users(client):
    client.post(
        "/users",
        json={"name": "A", "email": "a@example.com", "age": 20, "address": "Kyoto"},
    )
    client.post(
        "/users",
        json={"name": "B", "email": "b@example.com", "age": 30, "address": "Nagoya"},
    )

    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_search_by_name(client):
    client.post(
        "/users",
        json={
            "name": "SearchMe",
            "email": "search@example.com",
            "age": 20,
            "address": "Sapporo",
        },
    )
    client.post(
        "/users",
        json={
            "name": "Other",
            "email": "other@example.com",
            "age": 40,
            "address": "Fukuoka",
        },
    )

    response = client.get("/users/search", params={"name": "SearchMe"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "SearchMe"


def test_search_by_email(client):
    client.post(
        "/users",
        json={
            "name": "EmailUser",
            "email": "find@example.com",
            "age": 35,
            "address": "Kobe",
        },
    )

    response = client.get("/users/search", params={"email": "find@example.com"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["email"] == "find@example.com"


def test_search_by_name_and_email(client):
    client.post(
        "/users",
        json={
            "name": "Dual",
            "email": "dual@example.com",
            "age": 28,
            "address": "Yokohama",
        },
    )
    client.post(
        "/users",
        json={
            "name": "Dual",
            "email": "other@example.com",
            "age": 33,
            "address": "Sendai",
        },
    )

    response = client.get(
        "/users/search", params={"name": "Dual", "email": "dual@example.com"}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["email"] == "dual@example.com"


def test_search_no_params_returns_all(client):
    client.post(
        "/users",
        json={"name": "X", "email": "x@example.com", "age": 20, "address": "A"},
    )
    response = client.get("/users/search")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 3: Run tests (requires Docker running)**

Run: `uv run pytest tests/ -v`
Expected: All tests pass.

**Step 4: Commit**

```bash
git add tests/
git commit -m "test: add user API integration tests"
```

---

### Task 9: Add .gitignore and final cleanup

**Files:**
- Create: `.gitignore`

**Step 1: Write .gitignore**

```
__pycache__/
*.pyc
.venv/
.env
```

**Step 2: Commit**

```bash
git add .gitignore
git commit -m "chore: add .gitignore"
```
