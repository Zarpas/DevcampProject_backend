from flask import Blueprint

from core import errors


bp = Blueprint("codelist_manager", __name__)

from core.codelist_manager import routes
