from flask import Blueprint

from core import errors


bp = Blueprint("auth", __name__)

from core.auth import routes
