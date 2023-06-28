from flask import Blueprint

from core import errors


bp = Blueprint("notes_manager", __name__)

from core.note_manager import routes
