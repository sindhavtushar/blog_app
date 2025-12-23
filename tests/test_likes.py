from application.models.db_service import (
    create_user, create_post, like_post, unlike_post
)


def test_like_unlike_post(session):
    user = create_user(
        id="u1",
        username="liker",
        email="like@test.com",
        password_hash="hash"
    )

    post = create_post(
        title="Post",
        content="Content",
        author_id=user.id
    )

    assert like_post(user.id, post.id) is True
    assert like_post(user.id, post.id) is False  # duplicate like

    assert unlike_post(user.id, post.id) is True
    assert unlike_post(user.id, post.id) is False
