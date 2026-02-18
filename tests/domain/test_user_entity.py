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
