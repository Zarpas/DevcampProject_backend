from functools import wraps

from flask import request, jsonify

from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from core import db
from core.errors import bad_request
from core.models import CodeList

from core.codelist_manager import bp


# need to add the listoperate wrapper
def listoperate_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["listoperate"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(message="List Operators Only!"), 403
        return decorator
    return wrapper

@bp.route('/codelist', methods=['POST'])
@listoperate_required()
def new_codelist():
    data = request.get_json() or {}
    if (
        "list_code" not in data
        or "description" not in data
        or "edition" not in data
        or "revision" not in data
        or "project" not in data):
        return bad_request("Must include list_code, description, edition, revision and project.")
    
    codelist = CodeList()
    codelist.from_dict(data)
    db.session.add(codelist)
    db.session.commit()

    response = jsonify(codelist.to_dict())
    response.status_code = 201
    return response


@bp.route('/codelist', methods=['GET'])
def get_codelist():
    if request.is_json and "id" in request.json:
        id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the message.")
    
    return jsonify(CodeList.query.get_or_404(id).to_dict())


@bp.route('/codelists', methods=['GET'])
def get_codelist_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    data = CodeList.to_collection_dict(CodeList.query, page, per_page, "codelist_manager.get_codelist_list")
    return jsonify(data)



@bp.route('/codelist', methods=['DELETE'])
@listoperate_required()
def delete_codelist():
    if request.is_json and "id" in request.json:
        id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the message.")

    codelist = CodeList.query.get(id)

    if codelist is None:
        return bad_request('List not found.')
    
    db.session.delete(codelist)
    db.session.commit()
    return jsonify({'message': 'List code deleted.'})