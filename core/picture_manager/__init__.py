from flask import Blueprint


bp = Blueprint("picture_manager", __name__)

from core.picture_manager import routes
