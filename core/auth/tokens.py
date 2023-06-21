from flask import jsonify
from flask import request
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request

from datetime import datetime
from datetime import timedelta
from datetime import timezone


from core import db, jwt
from core.models import User
from core.auth.users import jwt_redis_blocklist


@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify(code="dave", err="I can't let you do that"), 401


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    token_in_redis = jwt_redis_blocklist.get(jti)
    return token_in_redis is not None


@jwt.additional_claims_loader
def add_claims_to_access_token(identity):
    user = db.session.get(User, identity)
    return {
        "admin": user.admin,
        "fileupload": user.fileupload,
        "listoperate": user.listoperate,
        "writenote": user.writenote,
        "takepicture": user.takepicture,
    }


