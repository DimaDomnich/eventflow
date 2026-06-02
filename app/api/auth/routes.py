from flask import request
import time
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
    decode_token,
)
from app.extensions import db, bcrypt, get_redis_client
from app.models.user import UserModel
from . import auth_blp

DEFAULT_TTL = 604800


@auth_blp.route("/register", methods=["POST"])
def register():

    json = request.get_json()
    email, password, full_name = (
        json["email"],
        json["password"],
        json["full_name"],
    )

    if UserModel.query.filter(UserModel.email == email).first():
        return {"message": "Email in use."}, 400

    hashed_pass = bcrypt.generate_password_hash(password).decode("utf-8")

    user = UserModel(email=email, password=hashed_pass, full_name=full_name)

    db.session.add(user)
    db.session.commit()

    return {"message": "User created successfully."}, 201


@auth_blp.route("/login", methods=["POST"])
def login():

    json = request.get_json()
    email, password = json["email"], json["password"]

    user = UserModel.query.filter(UserModel.email == email).first()
    if not user:
        return {"message": "Invalid credentials."}, 401

    try:
        if not bcrypt.check_password_hash(user.password, password):
            return {"message": "Invalid credentials."}, 401
    except ValueError:
        return {"message": "Invalid credentials."}, 401

    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    refresh_jti = decode_token(refresh_token)["jti"]

    redis = get_redis_client()
    redis.set(f"refresh_token:{refresh_jti}", "1", ex=DEFAULT_TTL)

    return {"access": access_token, "refresh": refresh_token}, 200


@auth_blp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    refresh_jti = get_jwt()["jti"]

    redis = get_redis_client()
    stored = redis.get(f"refresh_token:{refresh_jti}")

    if not stored:
        return {"message": "Token expired or it doesn't match."}, 400

    new_access = create_access_token(str(get_jwt_identity()))

    return {"access": new_access}, 200


@auth_blp.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    jwt_data = get_jwt()
    access_jti, exp = jwt_data["jti"], jwt_data["exp"]

    remaining = int(exp - time.time())

    redis = get_redis_client()
    redis.set(f"blacklist:{access_jti}", "1", ex=remaining)

    refresh_token = request.headers.get("X-Refresh-Token")
    refresh_data = decode_token(refresh_token)

    refresh_jti, refresh_exp = refresh_data["jti"], refresh_data["exp"]
    refresh_remaining = int(refresh_exp - time.time())
    redis.delete(f"refresh_token:{refresh_jti}")
    redis.set(f"blacklist:{refresh_jti}", "1", ex=refresh_remaining)

    return {"message": "Logged out successfully."}, 200
