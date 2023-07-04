import os
from dotenv import load_dotenv
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config(object):
    TESTING = False
    DB_SERVER = '127.0.0.1'

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"sqlite:///" + os.path.join(basedir, "database.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY")

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    UPLOAD_FOLDER = os.path.join(basedir, "core/static/uploads")
    ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx", "ods"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = []

    REDIS_URL = os.environ.get("REDIS_URL") or "redis://"

    CORS_SUPPORTS_CREDENTIALS = True
    CORS_METHODS = ["GET", "HEAD", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"]

    # ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL")


class ProductionConfiguration(Config):
    """Uses production database server."""
    pass

class DevelopmentConfiguration(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "database.db")

    ADMINS = ["igor@example.com"]


class TestConfiguration(Config):
    TESTING = True
    DB_SERVER = 'localhost'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, "tests/database.sqlite")