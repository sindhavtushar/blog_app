
# application/__init__.py
from flask import Flask
from .database import db
from .config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)

    # migrate.init_app(app, db)

    # Import models here to register them with SQLAlchemy
    from application.models import db_tables

    # Register Blueprints
    from application.views.blog import blog_bp
    app.register_blueprint(blog_bp)

    return app