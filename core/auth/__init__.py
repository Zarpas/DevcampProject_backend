from functools import wraps

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
from flask_jwt_extended import set_refresh_cookies
from flask_jwt_extended import unset_jwt_cookies
from flask_jwt_extended import verify_jwt_in_request
    # get_csrf_token,
from flask_jwt_extended import get_jwt

from .. import db, jwt
from ..models import User, user_schema, users_schema

ACCESS_EXPIRES = timedelta(hours=1)

auth = Blueprint("auth", __name__)


# @auth.route("/user", methods=["POST"])
# def register():
#     id = request.json.get("id")
#     name = request.json.get("name")
#     surnames = request.json.get("surnames")
#     email = request.json.get("email")
#     password = request.json.get("password")

#     user = User(id=id, name=name, surnames=surnames, email=email, password=password)

#     if user is None:
#         return jsonify({"msg": "Something went wrong with user register"}), 400

#     db.session.add(user)
#     db.session.commit()
#     return user_schema.jsonify(user), 201


# @auth.route("/user", methods=["GET"])
# @jwt_required()
# def get_user():
#     id = get_jwt_identity()

#     user = User.query.get(id)

#     if user.can_admin:
#         if request.is_json:
#             id = request.json.get("id", None)
#             if id is not None:
#                 user = User.query.get(id)

#     return user_schema.jsonify(user), 200


# @auth.route("/user", methods=["PATCH"])
# @jwt_required()
# def user_admin():
#     id = get_jwt_identity()
#     admin = User.query.get(id)

#     if admin.can_admin is False:
#         return jsonify({"msg": "not necessary rights for this"}), 401

#     user_id = request.json.get("id")
#     user = User.query.get(user_id)
#     can_admin = request.json.get("can_admin", None)
#     if can_admin is not None:
#         user.can_admin = can_admin
#     can_fileupload = request.json.get("can_fileupload", None)
#     if can_fileupload is not None:
#         user.can_fileupload = can_fileupload
#     can_listoperate = request.json.get("can_listoperate", None)
#     if can_listoperate is not None:
#         user.can_listoperate = can_listoperate
#     can_writenote = request.json.get("can_writenote", None)
#     if can_writenote is not None:
#         user.can_writenote = can_writenote
#     can_takepicture = request.json.get("can_takepicture", None)
#     if can_takepicture is not None:
#         user.can_takepicture = can_takepicture
#     active = request.json.get("active", None)
#     if active is not None:
#         user.active = active

#     db.session.add(user)
#     db.session.commit()
#     return user_schema.jsonify(user), 200


# @auth.route("/get_users", methods=["GET"])
# @jwt_required()
# def get_user_list():
#     admin_id = get_jwt_identity()
#     admin = User.query.get(admin_id)
#     page = request.json.get("page", 1) -1
#     per_page = request.json.get("per_page", 1) 

#     if admin.can_admin is False:
#         return jsonify({"msg": "not necessary rights for this"}), 401
    
#     users = User.query.with_entities(User.id, User.name, User.surnames).all()[page*per_page:(page*per_page)+per_page]
#     return users_schema.jsonify(users)


# @auth.route("/token", methods=["POST"])
# def login():
#     id = request.json.get("id", None)
#     password = request.json.get("password", None)
#     user = User.query.get(id)
#     response = jsonify({"msg": "user not found or incorrect password!"})
#     if user is None:
#         return response, 401
#     if not user.verify_password(password):
#         return response, 401
#     new_token = create_access_token(identity=user.id, fresh=False)
#     new_refresh_token = create_refresh_token(identity=user.id)
#     response = jsonify(
#         {
#             "login": True,
#             "status": "created",
#             "meta": {
#                 "accessToken": new_token,
#                 # "access_csrf_token": get_csrf_token(new_token),
#                 "refreshToken": new_refresh_token,
#                 # "refresh_csrf_token": get_csrf_token(new_refresh_token)
#             },
#         }
#     )
#     set_access_cookies(response, new_token)
#     set_refresh_cookies(response, new_refresh_token)
#     return response, 200




# @auth.after_request
# def refresh(response):
#     try:
#         exp_timestamp = get_jwt()["exp"]
#         now = datetime.now(timezone.utc)
#         target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
#         if target_timestamp > exp_timestamp:
#             access_token = create_access_token(identity=get_jwt_identity())
#             set_access_cookies(response, access_token)
#         return response
#     except (RuntimeError, KeyError):
#         return response


# @auth.route("/logout", methods=["DELETE"])
# @jwt_required(optional=True)
# def logout():
#     id = verify_jwt_in_request(optional=True)
#     resp = jsonify({"logout": True})
#     unset_jwt_cookies(resp)
#     return resp, 200


# @auth.route("/new_password", methods=["PATCH"])
# @jwt_required()
# def new_password():
#     id = get_jwt_identity()
#     print(id)
#     user = User.query.get(id)
#     old_password = request.json.get("old_password")
#     new_password = request.json.get("new_password")
#     if user.verify_password(old_password):
#         user.password_hash = user.hash_password(new_password)
#         db.session.add(user)
#         db.session.commit()
#         return user_schema.jsonify(user), 200

#     return jsonify({"msg": "password incorrect"}), 400


# @auth.route("/logged_in", methods=["GET"])
# @jwt_required(optional=True)
# def logged_in():
#     if verify_jwt_in_request(optional=True):
#         return jsonify({"logged_in": True}), 200
#     else:
#         return jsonify({"logged_in": False}), 200


##################################################################################
# new code addition
##################################################################################

# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


# Setup our redis connection for storing the blocklisted tokens. You will probably
# want your redis instance configured to persist data to disk, so that a restart
# does not cause your application to forget that a JWT was revoked.
jwt_redis_blocklist = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


# Here is a custom decorator that verifies the JWT is present in the request,
# as well as insuring that the JWT has a claim indicating that this user is
# an administrator
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


# Set a callback function to return a custom response whenever an expired
# token attempts to access a protected route. This particular callback function
# takes the jwt_header and jwt_payload as arguments, and must return a Flask
# response. Check the API documentation to see the required argument and return
# values for other callback functions.
@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify(code="dave", err="I can't let you do that"), 401


# Callback function to check if a JWT exists in the redis blocklist
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
        "can_takepicture": user.can_takepicture
    }


# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@auth.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            # set_access_cookies(response, access_token)  # remake to use tokens only
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


# We are using the `refresh=True` options in jwt_required to only allow
# refresh tokens to access this route.
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

    # Notice that we are passing in the actual sqlalchemy user object here
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth.route("/logout", methods=["DELETE"])
@jwt_required(verify_type=False)
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    jwt_redis_blocklist.set(jti, "", ex=ACCESS_EXPIRES)

    # Returns "Access token revoked" or "Refresh token revoked"
    return jsonify(msg=f"{ttype.capitalize()} token successfully revoked")


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@auth.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@auth.route("/who_am_i", methods=["GET"])
@jwt_required()
def protected_who_am_i():
    # We can now access our sqlalchemy User object via `current_user`.
    return jsonify(
        id=current_user.id,
        name=current_user.name,
        surnames=current_user.surnames,
    )


# In a protected view, get the claims you added to the jwt with the
# get_jwt() method
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
