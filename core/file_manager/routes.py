from core.models import User, File
from flask import jsonify, request, abort
import os
from werkzeug.utils import secure_filename
from flask_jwt_extended import get_jwt_identity

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from core import db
import config
from core.file_manager import bp
from core.errors import bad_request


UPLOAD_DIRECTORY = config.Config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = config.Config.ALLOWED_EXTENSIONS

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


def file_upload_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["fileupload"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(message="File Uploaders only!"), 403

        return decorator

    return wrapper


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# uploads a file from de the frontend (form-data, no json in the body)
@bp.route("/file", methods=["POST"])
@file_upload_required()
def post_file():
    if "filename" not in request.files:
        return bad_request("No file part")
    filename = request.files["filename"]
    if filename.filename == "":
        return bad_request("No selected file")

    id = get_jwt_identity()
    user = User.query.get(id)

    if filename and allowed_file(filename.filename):
        # todo: check if the file already exists.
        filename.save(
            os.path.join(UPLOAD_DIRECTORY, secure_filename(filename.filename))
        )
        file = File()
        file.filename = os.path.join(UPLOAD_DIRECTORY, secure_filename(filename.filename))
        file.sender_id = user.id
        
        db.session.add(file)
        db.session.commit()
    else:
        return bad_request("Not allowed filetype")

    return jsonify(file.to_dict())


@bp.route("/files", methods=["GET"])
@file_upload_required()
def get_file_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    data = File.to_collection_dict(
        File.query, page, per_page, "file_manager.get_file_list"
    )

    return jsonify(data)


@bp.route("/file", methods=["GET"])
@file_upload_required()
def get_file():
    if request.is_json:
        if "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the file.")
    return jsonify(File.query.get_or_404(id).to_dict())


@bp.route("/file", methods=["DELETE"])
@file_upload_required()
def delete_file():
    if request.is_json:
        if "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the file.")
    
    file = File.query.get(id)

    if file is None:
        return bad_request("file not found")
    
    response = {}
    try:
        os.remove(file.filename)
    except FileNotFoundError:
        response["error"] = "file not found"
    
    db.session.delete(file)
    db.session.commit()
    response["message"] = "file deleted"
    return response
    
