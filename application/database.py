# application/database.py
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Initialize extension with your custom Base class
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
