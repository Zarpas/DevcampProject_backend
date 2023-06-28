from flask import Blueprint

from core import errors


bp = Blueprint("auth_manager", __name__)

from core.auth_manager import routes
