from flask import jsonify, request, Blueprint

from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

from .. import app
from ..models import User, user_schema

auth = Blueprint("auth", __name__)


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

    access_token = create_access_token(identity=id)
    refresh_token = create_refresh_token(identity=id)

    response = jsonify({"login": True})
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    return response, 200


@auth.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    response = jsonify({"refresh": True})
    set_access_cookies(response, access_token)
    return response, 200


@auth.route("/remove", methods=["POST"])
def logout():
    resp = jsonify({"logout": True})
    unset_jwt_cookies(resp)
    return resp, 200


@auth.route("/example", methods=["GET"])
@jwt_required()
def protected():
    username = get_jwt_identity()
    return jsonify({"hello": "from {}".format(username)}), 200
