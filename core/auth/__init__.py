from flask import Blueprint


bp = Blueprint("auth", __name__)

from core.auth import errors, routes
