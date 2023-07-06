from flask import jsonify, request

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity

from core import db

from core.task_manager import bp
from core.models import User, Task
from core.errors import bad_request

def task_manager_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["listoperate"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(message="List Operators only!"), 403

        return decorator

    return wrapper

@bp.route("/task", methods=['GET'])
@task_manager_required()
def get_task():
    if request.is_json and "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the task.")
    
    return jsonify(Task.query.get_or_404(id).to_dict())


@bp.route("/task", methods=["POST"])
@task_manager_required()
def new_task():
    id = get_jwt_identity()
    user = User.query.get(id)
    task = request.json.get("task", None)
    description = request.json.get("description", "")
    filename = request.json.get("filename", None)
    if task is None:
        return bad_request("No task especified")
    if filename is None:
        return bad_request("File not especified")
    if user.get_task_in_progress(task):
        return bad_request("A {} task is currently in progress".format(task))
    else:
        user.launch_task(task, description, filename)
        db.session.commit()
    return jsonify({"message": "task launched"})


@bp.route("/tasks", methods=["GET"])
@task_manager_required()
def get_task_list():
    id = get_jwt_identity()
    user = User.query.get(id)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    active = request.args.get("active", False, type=bool)

    if active is True:
        data = Task.to_collection_dict(
        user.get_tasks_in_progress(), page, per_page, "task_manager.get_task_list"
    )
    else:
        data = Task.to_collection_dict(
        Task.query.filter_by(user=user), page, per_page, "task_manager.get_task_list"
    )

    return jsonify(data)


