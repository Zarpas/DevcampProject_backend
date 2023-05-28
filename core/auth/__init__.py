from functools import wraps

import json

from flask import jsonify
from flask import request
from flask import Blueprint

from flask_jwt_extended import current_user

from datetime import datetime
from datetime import timedelta
from datetime import timezone

import redis

from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import get_jwt

from pprint import pprint

from .. import db, jwt
from ..models import User, user_schema, users_schema

ACCESS_EXPIRES = timedelta(hours=1)

auth = Blueprint("auth", __name__)


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims["can_admin"]:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg="Admins only!"), 403

        return decorator

    return wrapper


@auth.route("/user", methods=["POST"])
def register():
    id = request.json.get("id")
    name = request.json.get("name")
    surnames = request.json.get("surnames")
    email = request.json.get("email")
    password = request.json.get("password")

    user = User(id=id, name=name, surnames=surnames, email=email, password=password)

    if user is None:
        return jsonify({"msg": "Something went wrong with user register"}), 400

    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user), 201


@auth.route("/user", methods=["GET"])
@admin_required()
def get_user():
    id = request.args.get("id", None)
    user = User.query.get(id)

    return user_schema.jsonify(user), 200


@auth.route("/user", methods=["PATCH"])
@admin_required()
def user_admin():
    user_id = request.json.get("id")
    user = User.query.get(user_id)
    active = request.json.get("active", None)
    if active is not None:
        user.active = active
    can_admin = request.json.get("can_admin", None)
    if can_admin is not None:
        user.can_admin = can_admin
    can_fileupload = request.json.get("can_fileupload", None)
    if can_fileupload is not None:
        user.can_fileupload = can_fileupload
    can_listoperate = request.json.get("can_listoperate", None)
    if can_listoperate is not None:
        user.can_listoperate = can_listoperate
    can_writenote = request.json.get("can_writenote", None)
    if can_writenote is not None:
        user.can_writenote = can_writenote
    can_takepicture = request.json.get("can_takepicture", None)
    if can_takepicture is not None:
        user.can_takepicture = can_takepicture

    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user), 200


@auth.route("/users", methods=["GET"])
@admin_required()
def get_user_list():
    page = int(request.args.get("page", 0))
    per_page = 10

    users = User.query.with_entities(User.id, User.name, User.surnames).all()[
        page * per_page : (page * per_page) + per_page
    ]
    return users_schema.jsonify(users)


@auth.route("/new_password", methods=["PATCH"])
@jwt_required()
def new_password():
    id = get_jwt_identity()
    user = User.query.get(id)
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    if user.check_password(old_password):
        user.password_hash = user.hash_password(new_password)
        db.session.add(user)
        db.session.commit()
        response = user_schema.dump(user)
        response["status"] = "created"
        return jsonify(response), 200

    return jsonify({"msg": "password incorrect"}), 400


@auth.route("/logged_in", methods=["GET"])
@jwt_required(optional=True)
def logged_in():
    if verify_jwt_in_request(optional=True):
        id = get_jwt_identity()
        user = User.query.get(id)
        return (
            jsonify(
                {
                    "logged_in": True,
                    "can_admin": user.can_admin,
                    "can_fileupload": user.can_fileupload,
                    "can_listoperate": user.can_listoperate,
                    "can_writenote": user.can_writenote,
                    "can_takepicture": user.can_takepicture,
                    "name": user.name
                }
            ),
            200,
        )
    else:
        return jsonify({"logged_in": False}), 200


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


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
        "can_admin": user.can_admin,
        "can_fileupload": user.can_fileupload,
        "can_listoperate": user.can_listoperate,
        "can_writenote": user.can_writenote,
        "can_takepicture": user.can_takepicture,
    }


@auth.after_request
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


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth.route("/login", methods=["POST"])
def login():
    id = request.json.get("id", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(id=id).one_or_none()
    if not user or not user.check_password(password):
        return jsonify("Wrong username or password"), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(
        access_token=access_token, refresh_token=refresh_token, status="created"
    )


@auth.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)

    # Returns "Access token revoked" or "Refresh token revoked"
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")


######################################################
# for test purposes only                             #
######################################################


@auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@auth.route("/who_am_i", methods=["GET"])
@jwt_required()
def protected_who_am_i():
    return jsonify(
        id=current_user.id,
        name=current_user.name,
        surnames=current_user.surnames,
    )


@auth.route("/protected_claims", methods=["GET"])
@jwt_required()
def protected_claims():
    claims = get_jwt()
    return jsonify(claims=claims)


@auth.route("/optionally_protected", methods=["GET"])
@jwt_required(optional=True)
def optionally_protected():
    current_identity = get_jwt_identity()
    if current_identity:
        return jsonify(logged_in_as=current_identity)
    else:
        return jsonify(logged_in_as="anonymous user")


@auth.route("/protected_admin", methods=["GET"])
@admin_required()
def protected_admin():
    return jsonify(foo="bar")
