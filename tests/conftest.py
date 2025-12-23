import os
import sys
import pytest
from flask import Flask

# PROJECT ROOT PATH ADD
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from application.database import db
from application.models.db_tables import Base


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        Base.metadata.create_all(db.engine)
        yield app
        db.session.remove()
        Base.metadata.drop_all(db.engine)


@pytest.fixture
def session(app):
    return db.session
