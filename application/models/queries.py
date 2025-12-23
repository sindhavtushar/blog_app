from application.models.db_tables import User
from application.database import db


def get_user_by_email(email):
    return db.session.query(User).filter(User.email == email).first()

# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    from application import create_app
    app = create_app()
    with app.app_context():
        user = get_user_by_email('john@example.com')
        print(user.username)