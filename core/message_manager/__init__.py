from flask import Blueprint


bp = Blueprint("message_manager", __name__)

from core.message_manager import routes
