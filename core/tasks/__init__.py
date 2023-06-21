from flask import Blueprint, jsonify, request

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity

from core import db

from core.models import User

bp = Blueprint("tasks_manager", __name__)


def tasks_manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["listoperate"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="List Operators only!"), 403

        return decorator

    return wrapper


@bp.route("/task", methods=["POST"])
@tasks_manager_required()
def new_task():
    id = get_jwt_identity()
    user = User.query.get(id)
    task = request.json.get('task', None)
    description = request.json.get('description', "")
    filename = request.json.get('filename', None)
    if task is None:
        return jsonify({"msg": "No task especified"})
    if filename is None:
        return jsonify({"msg": "File not especified"})
    if user.get_task_in_progress("example"):
        return jsonify({"msg": "A task is currently in progress"})
    else:
        user.launch_task(task, description, filename)
        db.session.commit()
    return jsonify({"msg": "task launched"})

