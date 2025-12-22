# application/config.py

import os
import secrets

class Config:
    
    SECRET_KEY = secrets.token_hex() 

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
