from flask import request, jsonify

from core import db 
from core.errors import bad_request 
from core.models import WireList
from core.wirelist_manager import bp

from core.codelist_manager.routes import listoperate_required


@bp.route('/wire', methods=['POST'])
@listoperate_required()
def new_wire():
    data = request.get_json() or {}

    if "owner_id" not in data:
        return bad_request("Must include owner_id.")

    wire = WireList()
    wire.from_dict(data, new_wire=True, owner=data["owner_id"])
    db.session.add(wire)
    db.session.commit()

    response = jsonify(wire.to_dict())
    response.status_code = 201
    return response


@bp.route('/wire', methods=['GET'])
def get_wire():
    if request.is_json and "id" in request.json:
        id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the wire.")
    
    return jsonify(WireList.query.get_or_404(id).to_dict())
    

@bp.route('/wires', methods=['GET'])
def get_wire_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    data = WireList.to_collection_dict(WireList.query, page, per_page, "wirelist_manager.get_wire_list")
    
    return jsonify(data)


@bp.route('/wire', methods=['PATCH'])
@listoperate_required()
def update_wire():
    # need to add some kind of check before commit
    data = request.get_json() or {}

    if "id" not in data:
        return bad_request("You need to identify the wire.")

    wire = db.session.get(WireList, data["id"])

    wire.from_dict(data)
    db.session.commit()

    return jsonify(wire.to_dict())


@bp.route('/wire', methods=['DELETE'])
@listoperate_required()
def delete_wire():
    if request.is_json and "id" in request.json:
        id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the wire.")
    
    wire = db.session.get(WireList, id)

    if wire is None:
        return bad_request("Wire not found.")
    
    response = {}
    db.session.delete(wire)
    db.session.commit()
    response["message"] = "Wire deleted"
    return response