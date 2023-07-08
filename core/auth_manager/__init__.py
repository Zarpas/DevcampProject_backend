from flask import Blueprint


bp = Blueprint("auth_manager", __name__)

from core.auth_manager import routes
