from flask import Blueprint


bp = Blueprint("file_manager", __name__)

from core.file_manager import files


