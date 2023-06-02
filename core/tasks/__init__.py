from flask import Blueprint, jsonify, request

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity

from .. import app
from .. import db

from ..models import User, user_schema, users_schema

tasks_mngr = Blueprint("tasks_manager", __name__)


def tasks_manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["can_listoperate"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="List Operators only!"), 403

        return decorator

    return wrapper


@tasks_mngr.route("/task", methods=["POST"])
@tasks_manager_required()
def new_task():
    id = get_jwt_identity()
    user = User.query.get(id)
    if user.get_task_in_progress("example"):
        return jsonify({"msg": "A task is currently in progress"})
    else:
        user.lauch_task("example", "task example")
        db.session.commit()
    return jsonify({"msg": "task launched"})
