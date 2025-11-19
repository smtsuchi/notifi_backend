import os
from datetime import timedelta

class Config():
    FLASK_APP = os.environ.get("FLASK_APP")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Force SQLite database for all environments
    # Render auto-sets DATABASE_URL to PostgreSQL, so we ignore it and use SQLite
    database_url = os.environ.get("DATABASE_URL", "sqlite:///notifi.db")

    # If Render sets a postgres URL, replace it with SQLite
    if database_url.startswith("postgres://") or database_url.startswith("postgresql://"):
        database_url = "sqlite:///notifi.db"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT  = False
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_ERROR_MESSAGE_KEY = "message"
    CORS_SUPPORTS_CREDENTIALS=True
