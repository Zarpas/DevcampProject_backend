from flask import Blueprint


bp = Blueprint("wirelist_manager", __name__)

from core.wirelist_manager import routes
