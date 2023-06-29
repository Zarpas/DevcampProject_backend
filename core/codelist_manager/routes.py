from flask import request, jsonify
from core import db
from core.errors import bad_request
from core.models import CodeList



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


def get_codelist():
    if request.is_json:
        if "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the message.")
    
    return jsonify(CodeList.query.get_or_404(id).to_dict())


def get_codelist_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    data = CodeList.to_collection_dict(CodeList.query, page, per_page, "codelist_manager.get_codelist_list")
    return jsonify(data)

def update_codelist():
    pass

def delete_codelist():
    pass