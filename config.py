import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Configuration(object):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/api/v1.0/token/refresh"
    JWT_COOKIE_CSRF_PROTECT = True
    UPLOAD_FOLDER = os.path.join(basedir, "core/static/uploads")
    ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx", "ods"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    REDIS_URL = os.environ.get("REDIS_URL") or "redis://"
