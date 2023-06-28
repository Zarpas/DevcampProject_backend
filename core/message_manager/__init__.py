from flask import Blueprint

from core import errors


bp = Blueprint("message_manager", __name__)

from core.message_manager import routes
