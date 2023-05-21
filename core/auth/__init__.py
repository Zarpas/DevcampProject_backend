from flask import jsonify, request, Blueprint

from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    verify_jwt_in_request,
    get_csrf_token,
)

from .. import db
from ..models import User, user_schema

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["POST"])
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


@auth.route("/auth", methods=["POST"])
def login():
    id = request.json.get("id", None)
    password = request.json.get("password", None)

    user = User.query.get(id)

    response = jsonify({"msg": "user not found or incorrect password!"})

    if user is None:
        return response, 401

    if not user.verify_password(password):
        return response, 401

    new_token = create_access_token(identity=user.id, fresh=False)
    new_refresh_token = create_refresh_token(identity=user.id)

    response = jsonify(
        {
            "login": True,
            "status": "created",
            "meta": {
                "accessToken": new_token,
                "access_csrf_token": get_csrf_token(new_token),
                "refreshToken": new_refresh_token,
                "refresh_csrf_token": get_csrf_token(new_refresh_token)
            },
        }
    )
    set_access_cookies(response, new_token)
    set_refresh_cookies(response, new_refresh_token)
    return response, 200


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    response = jsonify({"refresh": True})
    set_access_cookies(response, access_token)
    return response, 200


@auth.route("/remove", methods=["DELETE"])
@jwt_required(optional=True)
def logout():
    id = verify_jwt_in_request(optional=True)
    resp = jsonify({"logout": True})
    unset_jwt_cookies(resp)
    return resp, 200


@auth.route("/example", methods=["GET"])
@jwt_required()
def protected():
    id = get_jwt_identity()
    user = User.query.get(id)
    return jsonify({"hello": "from {}".format(user.name + " " + user.surnames)}), 200


@auth.route("/new_password", methods=["POST"])
@jwt_required()
def new_password():
    id = get_jwt_identity()
    user = User.query.get(id)
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    if user.verify_password(old_password):
        user.password_hash = user.hash_password(new_password)
        db.session.add(user)
        db.session.commit()
        return user_schema.jsonify(user), 200

    return jsonify({"msg": "password incorrect"}), 400


@auth.route("/user_admin", methods=["POST"])
@jwt_required()
def user_admin():
    id = get_jwt_identity()
    admin = User.query.get(id)

    if admin.can_admin is False:
        return jsonify({"msg": "not necessary rights for this"}), 401

    user_id = request.json.get("id")
    user = User.query.get(user_id)
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
    active = request.json.get("active", None)
    if active is not None:
        user.active = active

    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user), 200


@auth.route("/logged_in", methods=["GET"])
@jwt_required(optional=True)
def logged_in():
    if verify_jwt_in_request(optional=True):
        return jsonify({"logged_in": True}), 200
    else:
        return jsonify({"logged_in": False}), 200
