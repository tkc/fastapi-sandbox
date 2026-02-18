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
