from sqlalchemy.exc import IntegrityError
from application.database import db
from application.models.db_tables import (
    User, Category, Post, Tag, Comment,
    Like, AuthToken, Session
)
from datetime import datetime


# USER SERVICES

def create_user(id, username, email, password_hash, is_admin=False):
    try:
        user = User(
            id=id,
            username=username,
            email=email,
            password_hash=password_hash,
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        return user
    except IntegrityError:
        db.session.rollback()
        return None


def get_user_by_id(user_id):
    return db.session.query(User).filter_by(id=user_id).first()


def get_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()


def verify_user_email(user):
    user.is_email_verified = True
    db.session.commit()
    return user



# CATEGORY SERVICES

def create_category(name, description=None):
    category = Category(name=name, description=description)
    db.session.add(category)
    db.session.commit()
    return category


def get_all_categories():
    return db.session.query(Category).all()


def get_category_by_id(category_id):
    return db.session.query(Category).filter_by(id=category_id).first()



# POST SERVICES

def create_post(title, content, author_id, category_id=None, is_published=False):
    post = Post(
        title=title,
        content=content,
        author_id=author_id,
        category_id=category_id,
        is_published=is_published
    )
    db.session.add(post)
    db.session.commit()
    return post


def get_post_by_id(post_id):
    return db.session.query(Post).filter_by(id=post_id).first()


def get_all_posts(published_only=False):
    query = db.session.query(Post)
    if published_only:
        query = query.filter(Post.is_published.is_(True))
    return query.order_by(Post.created_at.desc()).all()


def update_post(post, **kwargs):
    for key, value in kwargs.items():
        if hasattr(post, key):
            setattr(post, key, value)
    post.updated_at = datetime.utcnow()
    db.session.commit()
    return post


def delete_post(post):
    db.session.delete(post)
    db.session.commit()



# TAG SERVICES

def get_or_create_tag(name):
    tag = db.session.query(Tag).filter_by(name=name).first()
    if not tag:
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
    return tag


def add_tags_to_post(post, tag_names):
    for name in tag_names:
        tag = get_or_create_tag(name)
        if tag not in post.tags:
            post.tags.append(tag)
    db.session.commit()
    return post



# COMMENT SERVICES

def add_comment(post_id, user_id, content):
    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content
    )
    db.session.add(comment)
    db.session.commit()
    return comment


def get_comments_for_post(post_id):
    return db.session.query(Comment).filter_by(post_id=post_id).all()



# LIKE SERVICES

def like_post(user_id, post_id):
    try:
        like = Like(user_id=user_id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def unlike_post(user_id, post_id):
    like = db.session.query(Like).filter_by(
        user_id=user_id,
        post_id=post_id
    ).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return True
    return False



# AUTH TOKEN SERVICES

def create_auth_token(user_id, token, token_type, expires_at):
    auth_token = AuthToken(
        user_id=user_id,
        token=token,
        type=token_type,
        expires_at=expires_at
    )
    db.session.add(auth_token)
    db.session.commit()
    return auth_token


def get_valid_token(token, token_type):
    return db.session.query(AuthToken).filter(
        AuthToken.token == token,
        AuthToken.type == token_type,
        AuthToken.is_used.is_(False),
        AuthToken.expires_at > datetime.utcnow()
    ).first()


def mark_token_used(auth_token):
    auth_token.is_used = True
    db.session.commit()



# SESSION SERVICES

def create_session(user_id, token, expires_at):
    session = Session(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.session.add(session)
    db.session.commit()
    return session


def get_session(token):
    return db.session.query(Session).filter(
        Session.token == token,
        Session.expires_at > datetime.utcnow()
    ).first()


def delete_session(session):
    db.session.delete(session)
    db.session.commit()
