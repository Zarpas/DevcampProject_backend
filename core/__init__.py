from flask import Flask, request, current_app
import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from redis import Redis
import rq
import os


db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()
mail = Mail()


def create_app(config_class=config.DevelopmentConfiguration):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    mail.init_app(app)
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue("micro-tasks", connection=app.redis)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    

    from core.auth_manager import bp as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/api/user/v1.0")

    from core.file_manager import bp as file_mngr_blueprint
    app.register_blueprint(file_mngr_blueprint, url_prefix="/api/file/v1.0")

    from core.task_manager import bp as task_mngr_blueprint
    app.register_blueprint(task_mngr_blueprint, url_prefix="/api/task/v1.0")

    from core.notification_manager import bp as notification_mngr_blueprint
    app.register_blueprint(notification_mngr_blueprint, url_prefix='/api/notification/v1.0')

    from core.message_manager import bp as message_mngr_blueprint
    app.register_blueprint(message_mngr_blueprint, url_prefix="/api/message/v1.0")

    from core.codelist_manager import bp as codelist_mngr_blueprint
    app.register_blueprint(codelist_mngr_blueprint, url_prefix="/api/codelist/v1.0")

    from core.wirelist_manager import bp as wirelist_mngr_blueprint
    app.register_blueprint(wirelist_mngr_blueprint, url_prefix="/api/wirelist/v1.0")

    from core.note_manager import bp as note_mngr_blueprint
    app.register_blueprint(note_mngr_blueprint, url_prefix="/api/note/v1.0")

    from core.picture_manager import bp as picture_mngr_blueprint
    app.register_blueprint(picture_mngr_blueprint, url_prefix="/api/picture/v1.0")


    if not app.debug:
        auth = None
        if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
            auth = (app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
        secure = None
        if app.config["MAIL_USE_TLS"]:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
            fromaddr="no-reply@" + app.config["MAIL_SERVER"],
            toaddrs=app.config["ADMINS"],
            subject="Backend Server Failure",
            credentials=auth,
            secure=secure,
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/server.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Backend Server startup")

    return app


from core import models
