from flask import request, jsonify

from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from core import db
from core.errors import bad_request
from core.models import Message, User

from core.message_manager import bp


@bp.route('/message', methods=['POST'])
@jwt_required()
def new_message():
    user_id = get_jwt_identity()

    data = request.get_json() or {}
    if (
        "recipient_id" not in data
        or "body" not in data):
        return bad_request("Must include recipient_id and body.")
    
    data["sender_id"] = user_id
    
    message = Message()
    message.from_dict(data)
    db.session.add(message)
    db.session.commit()

    response = jsonify(message.to_dict())
    response.status_code = 201
    return response


@bp.route('/message', methods=['GET'])
@jwt_required()
def get_message():
    if request.is_json and "id" in request.json:
            id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the message.")
    
    message = Message.query.get_or_404(id)
    user_id = get_jwt_identity()
    if message.sender_id==user_id or message.recipient_id==user_id:
        return jsonify(Message.query.get_or_404(id).to_dict())
    else:
         return bad_request("This message isn't for you.")


@bp.route('/messages', methods=['GET'])
@jwt_required()
def get_message_list():
    id = get_jwt_identity()
    user = db.session.get(User, id)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    sent = request.args.get("sent", False, type=bool)

    if sent is True:
        data = Message.to_collection_dict(
        Message.query.filter_by(author=user), page, per_page, "message_manager.get_message_list"
    )
    else:
        data = Message.to_collection_dict(
        Message.query.filter_by(recipient=user), page, per_page, "message_manager.get_message_list"
    )

    return jsonify(data)


@bp.route('/message', methods=['DELETE'])
@jwt_required()
def delete_message():
    if request.is_json and "id" in request.json:
        id = request.json.get("id", None)
    elif "id" in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request("You need to identify the message.")

    message = db.session.get(Message, id)
    if message is None:
        return bad_request('Message not found.')
    
    user_id = get_jwt_identity()
    if message.recipient_id != user_id:
        return bad_request("This message isn't yours.")
    
    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'message deleted.'})