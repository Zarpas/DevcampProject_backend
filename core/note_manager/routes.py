from functools import wraps

from flask import jsonify
from flask import request

from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity

from core import db
from core.note_manager import bp
from core.models import Note
from core.errors import bad_request

def writenote_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["writenote"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(message="Note writers only!"), 403

        return decorator

    return wrapper

@bp.route('/note', methods=['POST'])
@writenote_required()
def new_note():
    data = request.get_json() or {}
    sender_id = get_jwt_identity()
    if (
        "note" not in data
        or "reference_id" not in data
        or "private" not in data
    ):
        return bad_request("Must include body, reference_id and private.")
    data["sender_id"] = sender_id
    
    note = Note()
    note.from_dict(data, new_note=True)
    db.session.add(note)
    db.session.commit()

    response = jsonify(note.to_dict())
    response.status_code = 201
    return response
    

@bp.route('/note', methods=['GET'])
def get_note():
    if request.is_json and "id" in request.json:
        id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the note.")

    return jsonify(Note.query.get_or_404(id).to_dict())


@bp.route('/notes', methods=['GET'])
@writenote_required()
def get_note_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    data = Note.to_collection_dict(Note.query, page, per_page, "note_manager.get_note_list")

    return jsonify(data)


@bp.route('/note', methods=['PATCH'])
@writenote_required()
def update_note():
    sender_id = get_jwt_identity()
    data = request.get_json() or {}

    if "id" not in data:
        return bad_request("You need to identify the note.")
    
    if "note" not in data and "private" not in data:
        return bad_request("must include")
    
    note = db.session.get(Note, data["id"])
    if note is None:
        return bad_request("Note not found.")

    if note.sender_id != sender_id:
        return bad_request("This note isn't yours.")
    
    note.from_dict(data)
    db.session.commit()

    response = jsonify(note.to_dict())
    return response


@bp.route('/note', methods=['DELETE'])
@writenote_required()
def delete_note():
    if request.is_json and "id" in request.json:
        id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the note.")
    
    sender_id = get_jwt_identity()
    
    note = db.session.get(Note, id)

    if note is None:
        return bad_request("Note not found.")
    
    if note.sender_id != sender_id:
        return bad_request("This note isn't yours.")
    
    response = {}
    db.session.delete(note)
    db.session.commit()
    response["message"] = "Note deleted"
    return response