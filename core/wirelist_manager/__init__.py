from flask import Blueprint

from core import errors


bp = Blueprint("wirelist_manager", __name__)

from core.wirelist_manager import routes
