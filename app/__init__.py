from flask import Flask
from config import Config
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
cors = CORS(app)
jwt = JWTManager(app)
scheduler = APScheduler(app=app)

scheduler.start()

from . import models

from .auth import auth
from .api import api
from . import scheduled_tasks

app.register_blueprint(auth)
app.register_blueprint(api)