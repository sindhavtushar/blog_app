from application.models.db_service import (
    create_user, get_user_by_email
)
import uuid


def test_create_user(session):
    user = create_user(
        id=str(uuid.uuid4()),
        username="john",
        email="john@example.com",
        password_hash="hashed"
    )

    assert user is not None
    assert user.username == "john"
    assert user.email == "john@example.com"


def test_get_user_by_email(session):
    create_user(
        id="123",
        username="alice",
        email="alice@example.com",
        password_hash="hashed"
    )

    user = get_user_by_email("alice@example.com")
    assert user is not None
    assert user.username == "alice"
