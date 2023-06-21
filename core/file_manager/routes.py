from core.models import User, File
from flask import jsonify, request, abort
import os
from werkzeug.utils import secure_filename
from flask_jwt_extended import get_jwt_identity

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from core import db
from config import Configuration
from core.file_manager import bp
from core.auth.errors import bad_request


UPLOAD_DIRECTORY = Configuration.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = Configuration.ALLOWED_EXTENSIONS

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
    # if "filename" not in request.files:
    #     return {"msg": "No file part"}, 400
    # filename = request.files["filename"]
    # id = get_jwt_identity()
    # if filename.filename == "":
    #     return {"msg": "No selected file"}, 412

    # if filename and allowed_file(filename.filename):
    #     filename.save(
    #         os.path.join(UPLOAD_DIRECTORY, secure_filename(filename.filename))
    #     )
    #     file = File(
    #         os.path.join(UPLOAD_DIRECTORY, secure_filename(filename.filename)), id
    #     )
    #     db.session.add(file)
    #     db.session.commit()
    # else:
    #     return {"msg": "Not allowed filetype"}, 415

    # return file_schema.jsonify(file)
    pass


@bp.route("/files", methods=["GET"])
@file_upload_required()
def list_files():
    # files = File.query.all()
    # print(files)
    # return files_schema.jsonify(files)
    pass


@bp.route("/file", methods=["GET"])
@file_upload_required()
def get_file():
    if request.is_json:
        if "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the user.")
    return  jsonify(File.query.get_or_404(id).to_dict())



@bp.route("/file", methods=["DELETE"])
@file_upload_required()
def delete_file():
    # id = request.json.get("id")
    # file = File.query.get(id)
    # if file is None:
    #     return {"msg": "file not found"}, 400
    # try:
    #     os.remove(file.filename)
    #     response = {}
    # except FileNotFoundError:
    #     response["error"] = "file not found"
    # db.session.delete(file)
    # db.session.commit()
    # response["msg"] = "file deleted"
    # return response
    pass
