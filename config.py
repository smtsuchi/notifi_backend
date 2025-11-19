import os
from datetime import timedelta

class Config():
    FLASK_APP = os.environ.get("FLASK_APP")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Database configuration
    # Uses PostgreSQL in production (via DATABASE_URL) or SQLite for local development
    database_url = os.environ.get("DATABASE_URL", "sqlite:///notifi.db")

    # Render uses 'postgres://' but SQLAlchemy 1.4+ requires 'postgresql://'
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT  = False
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_ERROR_MESSAGE_KEY = "message"
    CORS_SUPPORTS_CREDENTIALS=True
