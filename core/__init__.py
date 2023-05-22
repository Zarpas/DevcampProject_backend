from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import logging

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
jwt = JWTManager(app)
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

logging.getLogger('flask_cors').level = logging.DEBUG

from .models import User, user_schema, users_schema

migrate = Migrate(app, db)

from .auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint, url_prefix="/api/token/v1.0")
