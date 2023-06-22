from flask import Blueprint


bp = Blueprint("task_manager", __name__)

from core.task_manager import routes, tasks
