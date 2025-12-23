from dotenv import load_dotenv
from flask_login import LoginManager

from application.models.db_tables import User
load_dotenv()   # ALWAYS load env when app module is imported

from flask import Flask
from application.config import Config
from application.database import db, migrate
import os

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    # print("URI FROM APP:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    db.init_app(app)
    migrate.init_app(app, db)

    # Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "authentication.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # load user from database

    from application.views.blog import blog_bp
    from application.views.auth import auth_bp
    app.register_blueprint(blog_bp)
    app.register_blueprint(auth_bp)

    return app
