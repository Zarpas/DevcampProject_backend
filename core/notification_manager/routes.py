from functools import wraps

from flask import jsonify
from flask import request

from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import current_user

import redis

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from core import db, jwt
from core.auth_manager import bp
from core.models import User
from core.errors import bad_request

from core.notification_manager import bp
from core.models import Notification

@bp.route('/notification', methods=['GET'])
@jwt_required(optional=True)
def get_notification():
    user_id = get_jwt_identity()
    if user_id:
        if request.is_json and "id" in request.json:
                id = request.json.get("id", None)
        elif "id" in request.args:
            id = request.args.get("id", None)
        else:
            return bad_request("You need to identify the notification.")
        
        user = db.session.get(User, user_id)

        return jsonify(Notification.query.get_or_404(id).to_dict())
    else:
        return bad_request("Registered users only.")

@bp.route('/notifications', methods=['GET'])
@jwt_required(optional=True)
def get_notification_list():
    id = get_jwt_identity()

    if id:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)

        user = db.session.get(User, id)

        data = Notification.to_collection_dict(
            Notification.query.filter_by(user=user), page, per_page, 
            "notification_manager.get_notification_list")

        return jsonify(data)
    else:
        return bad_request("Registered users only.")

