from functools import wraps

from flask import jsonify
from flask import request

from werkzeug.utils import secure_filename

from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity

import os

from core import db
import config
from core.picture_manager import bp
from core.models import Picture
from core.errors import bad_request

UPLOAD_DIRECTORY = config.Config.UPLOAD_PICTURE_FOLDER
ALLOWED_EXTENSIONS = config.Config.ALLOWED_PICTURE_EXTENSIONS


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def takepicture_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["takepicture"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(message="Picture takers only!"), 403

        return decorator

    return wrapper


@bp.route("/picture", methods=['POST'])
@takepicture_required()
def new_picture():
    if "filename" not in request.files:
        return bad_request("No file part")
    filename = request.files["filename"]
    if filename.filename == "":
        return bad_request("No selected file")
    
    data = {}
    if "reference_id" in request.args:
        data["reference_id"] = request.args.get("reference_id", None)
    if "description" in request.args:
        data["description"] = request.args.get("description", None)
    print(data)

    if ("reference_id" not in data or "description" not in data):
        return bad_request("Must include")

    id = get_jwt_identity()
    directory = UPLOAD_DIRECTORY + '/{}'.format(id)
    
    if filename and allowed_file(filename.filename):
        # todo: check if the file already exists.
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename.save(
            os.path.join(directory, secure_filename(filename.filename))
        )
        
        data["picture"] = os.path.join(directory, secure_filename(filename.filename))
        data["sender_id"] = id
        picture = Picture()
        picture.from_dict(data, new_picture=True)
        
        db.session.add(picture)
        db.session.commit()
    else:
        return bad_request("Not allowed filetype")

    return jsonify(picture.to_dict())


@bp.route('/picture', methods=['GET'])
def get_picture():
    if request.is_json and "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the file.")
    return jsonify(Picture.query.get_or_404(id).to_dict())


@bp.route('/pictures', methods=['GET'])
def get_picture_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    reference_id = request.args.get("reference_id", "")

    if reference_id == "":
        return bad_request("Must identify the code list refered.")

    data = Picture.to_collection_dict(
        Picture.query.filter_by(reference_id=reference_id), page, per_page, "picture_manager.get_picture_list", reference_id=reference_id
    )

    return jsonify(data)


@bp.route('/picture', methods=['PATCH'])
@takepicture_required()
def update_picture():
    data = request.get_json() or {}

    user_id = get_jwt_identity()

    if "id" not in data:
        return bad_request("You need to identify the picture.")
    
    if "description" not in data:
        return bad_request("Must include description.")
    
    picture = db.session.get(Picture, data["id"])
    if picture is None:
        return bad_request("Picture not found.")
    
    picture.from_dict(data)
    db.session.commit()

    return jsonify(picture.to_dict())


@bp.route('/picture', methods=['DELETE'])
@takepicture_required()
def delete_picture():
    if request.is_json and "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the picture.")
    
    picture = db.session.get(Picture, id)

    if picture is None:
        return bad_request("picture not found")
    
    user_id = get_jwt_identity()
    if picture.sender_id != user_id:
        return bad_request("This picture isn't yours.")
    
    response = {}
    try:
        os.remove(picture.picture)
    except FileNotFoundError:
        response["error"] = "picture not found"
    
    db.session.delete(picture)
    db.session.commit()
    response["message"] = "picture deleted"
    return response
