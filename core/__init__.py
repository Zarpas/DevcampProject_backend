from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import logging
from redis import Redis
import rq

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
jwt = JWTManager(app)
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('micro-tasks', connection=app.redis)

logging.getLogger("flask_cors").level = logging.DEBUG

from .models import User, user_schema, users_schema
from .models import File, files_schema, file_schema
from .models import Task, task_schema, tasks_schema
from .models import List, list_schema, lists_schema
from .models import WireList, wirelist_schema, wirelists_schema

migrate = Migrate(app, db)

from .auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint, url_prefix="/api/user/v1.0")

from .file_manager import file_mngr as file_mngr_blueprint

app.register_blueprint(file_mngr_blueprint, url_prefix="/api/file/v1.0")
