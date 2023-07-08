from flask import Blueprint


bp = Blueprint("codelist_manager", __name__)

from core.codelist_manager import routes
