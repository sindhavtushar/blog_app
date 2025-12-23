# application/mdodels/db_service.py

from flask import current_app
from application.database import db
from application.models.db_tables import Category, User

def create_user(username, email, password_hash, is_admin=False):
    try:
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            is_admin=is_admin
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user
    except Exception as e:
        db.session.rollback()
        print(f"Error creating user: {e}")
        return None
