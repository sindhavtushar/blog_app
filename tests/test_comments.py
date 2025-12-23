from application.models.db_service import (
    create_user, create_post, add_comment, get_comments_for_post
)


def test_add_comment(session):
    user = create_user(
        id="u1",
        username="user1",
        email="u1@test.com",
        password_hash="hash"
    )

    post = create_post(
        title="Post",
        content="Content",
        author_id=user.id
    )

    comment = add_comment(
        post_id=post.id,
        user_id=user.id,
        content="Nice post"
    )

    assert comment.id is not None
    assert comment.content == "Nice post"


def test_get_comments(session):
    user = create_user(
        id="u2",
        username="user2",
        email="u2@test.com",
        password_hash="hash"
    )

    post = create_post(
        title="Post",
        content="Content",
        author_id=user.id
    )

    add_comment(post.id, user.id, "One")
    add_comment(post.id, user.id, "Two")

    comments = get_comments_for_post(post.id)
    assert len(comments) == 2
