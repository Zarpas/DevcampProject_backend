from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
jwt = JWTManager(app)
ma = Marshmallow(app)

migrate = Migrate(app, db)

@app.route("/")
def hello():
    return {"msg": "hello word"}, 200