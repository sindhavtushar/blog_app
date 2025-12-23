from application.models.db_service import (
    create_user, create_post, get_post_by_id
)
import uuid


def test_create_post(session):
    user = create_user(
        id=str(uuid.uuid4()),
        username="author",
        email="author@test.com",
        password_hash="hash"
    )

    post = create_post(
        title="Test Post",
        content="Hello World",
        author_id=user.id
    )

    assert post.id is not None
    assert post.title == "Test Post"
    assert post.author_id == user.id


def test_get_post_by_id(session):
    user = create_user(
        id="u1",
        username="test",
        email="test@test.com",
        password_hash="hash"
    )

    post = create_post(
        title="Find Me",
        content="content",
        author_id=user.id
    )

    found = get_post_by_id(post.id)
    assert found is not None
    assert found.title == "Find Me"
