import os
from datetime import timedelta

class Config():
    FLASK_APP = os.environ.get("FLASK_APP")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # SQLite database configuration (development)
    # For production, set DATABASE_URL environment variable to PostgreSQL connection string
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///notifi.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_COOKIE_SECURE = True
    JWT_COOKIE_CSRF_PROTECT  = False
    JWT_TOKEN_LOCATION = ["cookies", "headers"]
    JWT_SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_ERROR_MESSAGE_KEY = "message"
    CORS_SUPPORTS_CREDENTIALS=True
