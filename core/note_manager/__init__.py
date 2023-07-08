from flask import Blueprint


bp = Blueprint("note_manager", __name__)

from core.note_manager import routes
