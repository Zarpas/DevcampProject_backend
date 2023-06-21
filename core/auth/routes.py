from functools import wraps
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt
from flask import jsonify
from flask import request
from flask_jwt_extended import current_user
import redis

from core.auth import bp
from core.auth.errors import bad_request

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from core import db, jwt
from core.models import User
from config import Configuration


ACCESS_EXPIRES = Configuration.JWT_ACCESS_TOKEN_EXPIRES


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["admin"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(message="Admins only!"), 403

        return decorator

    return wrapper


@bp.route("/user", methods=["POST"])
def register():
    data = request.get_json() or {}
    if 'id' not in data or 'username' not in data or 'surnames' not in data or 'email' not in data or 'password' not in data:
        return bad_request('Must include ID, username, surnames, email and password')
    if User.query.filter_by(id=data['id']).first():
        return bad_request('Please use a different ID')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address')
    
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()

    response = jsonify(user.to_dict())
    response.status_code = 201
    return response


@bp.route("/user", methods=["GET"])
@admin_required()
def get_user():
    if request.is_json:
        if 'id' in request.json:
            id = request.json.get("id", None)
    elif 'id' in request.args:
        id = request.args.get("id", None)
    else:
        return bad_request('You need to identify the user.')

    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route("/user", methods=["PATCH"])
@admin_required()
def user_admin():
    data = request.get_json() or {}
    user = User.query.get_or_404(data['id'])
    
    if 'username' in data and data['username'] != user.username and 'surnames' in data and data['surnames'] != user.surnames:
        return bad_request('You can not change your name')
    if 'email' in data and data['email'] != user.email and User.query.filter_by(email=data['email']).first():
        return bad_request('Please use a different email address.')
    
    user.from_dict(data, new_user=False, change_admin=True)
    db.session.commit()
    return jsonify(user.to_dict())


@bp.route("/users", methods=["GET"])
@admin_required()
def get_user_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    data = User.to_collection_dict(User.query, page, per_page, 'auth.get_user_list')

    return jsonify(data)


@bp.route("/search_user", methods=["GET"])
@admin_required()
def search_user():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    user_id = request.args.get("id", None)
    name = request.args.get("username", None)
    surnames = request.args.get("surnames", None)


    if user_id is not None:
        users = User.query.filter(User.id.like("%"+user_id+"%"))
    elif name is not None:
        users = User.query.filter(User.username.like("%"+name+"%"))
    elif surnames is not None:
        users = User.query.filter(User.surnames.like("%"+surnames+"%"))
    else:
        return bad_request("no data sent")
    data = User.to_collection_dict(users, page, per_page, 'auth.search_user')
    return jsonify(data)


@bp.route("/new_password", methods=["PATCH"])
@jwt_required()
def new_password():
    id = get_jwt_identity()
    user = User.query.get(id)
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    if user.check_password(old_password):
        user.hash_password(new_password)
        db.session.commit()
        return jsonify(user.to_dict()), 200

    return bad_request('Wrong password')


@bp.route("/logged_in", methods=["GET"])
@jwt_required(optional=True)
def logged_in():
    if verify_jwt_in_request(optional=True):
        id = get_jwt_identity()
        user = User.query.get(id)
        response = user.to_dict(include_roles=True)
        response['logged_in'] = True
        return jsonify(response)
    else:
        return jsonify({"logged_in": False}), 200


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

@bp.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@bp.route("/login", methods=["POST"])
def login():
    id = request.json.get("id", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(id=id).one_or_none()
    if not user or not user.check_password(password):
        return bad_request("Wrong username or password")

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(
        access_token=access_token, refresh_token=refresh_token, status="created"
    )


jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


@bp.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)

    # Returns "Access token revoked" or "Refresh token revoked"
    return jsonify(message=f"{ttype.capitalize()} token successfully revoked")

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


######################################################
# for test purposes only                             #
######################################################


# @bp.route("/protected", methods=["GET"])
# @jwt_required()
# def protected():
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200


@bp.route("/who_am_i", methods=["GET"])
@jwt_required()
def protected_who_am_i():
    return jsonify(
        id=current_user.id,
        name=current_user.username,
        surnames=current_user.surnames,
    )


# @bp.route("/protected_claims", methods=["GET"])
# @jwt_required()
# def protected_claims():
#     claims = get_jwt()
#     return jsonify(claims=claims)


@bp.route("/optionally_protected", methods=["GET"])
@jwt_required(optional=True)
def optionally_protected():
    current_identity = get_jwt_identity()
    if current_identity:
        return jsonify(logged_in_as=current_identity)
    else:
        return jsonify(logged_in_as="anonymous user")


# @bp.route("/protected_admin", methods=["GET"])
# @admin_required()
# def protected_admin():
#     return jsonify(foo="bar")
