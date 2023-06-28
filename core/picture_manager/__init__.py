from flask import Blueprint

from core import errors


bp = Blueprint("picture_manager", __name__)

from core.picture_manager import routes
