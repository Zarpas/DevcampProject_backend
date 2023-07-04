from flask import request, jsonify
from core import db
from core.errors import bad_request
from core.models import Message

from core.message_manager import bp


@bp.route('/message', methods=['POST'])
def new_message():
    data = request.get_json() or {}
    if (
        "sender_id" not in data
        or "recipient_id" not in data
        or "body" not in data):
        return bad_request("Must include sender_id, recipient_id and body.")
    
    message = Message()
    message.from_dict(data)
    db.session.add(message)
    db.session.commit()

    response = jsonify(message.to_dict())
    response.status_code = 201
    return response


@bp.route('/message', methods=['GET'])
def get_message():
    if request.is_json:
        if "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the message.")
    
    return jsonify(Message.query.get_or_404(id).to_dict())


@bp.route('/messages', methods=['GET'])
def get_message_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    data = Message.to_collection_dict(Message.query, page, per_page, "message_manager.get_message_list")
    return jsonify(data)


@bp.route('/delete_message', methods=['DELETE'])
def delete_message():
    if request.is_json:
        if "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)

    message = Message.query.get(id)
    if message is None:
        return bad_request('Message not found.')
    
    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'message deleted.'})