import os

from datetime import timedelta
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import (
    UserSignup,
    User,
    UserLogin,
    UserLogout,
    TokenRefresh,
)
from resources.item import Item, Items
from resources.store import Store, Stores
from blacklist import BLACKLIST
from db import db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///data.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.secret_key = "nigel"
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {"is_admin": True}
    return {"is_admin": False}


@jwt.token_in_blacklist_loader
def check_if_blacklisted(decrypted_token):
    return decrypted_token["jti"] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return (
        jsonify(
            {"description": "The token has expired", "error": "token expired"}
        ),
        401,
    )


@jwt.invalid_token_loader  # used when token isn't jwt format
def invalid_token_callback(erro):
    return jsonify({"message": "what are you doing!"}), 401


#  @jwt.unauthorized_loader used when token is missing
#  @jwt.needs_fresh_token_loader used when fresh token is needed
#  @jwt.revoked_token_loader used when loging out

app.config["JWT_EXPIRATION_DELTA"] = timedelta(seconds=3600)

api.add_resource(Item, "/item/<string:name>")
api.add_resource(Items, "/items")
api.add_resource(UserSignup, "/signup")
api.add_resource(Store, "/store/<string:name>")
api.add_resource(Stores, "/stores")
api.add_resource(User, "/user/<int:user_id>")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(TokenRefresh, "/refresh")

if __name__ == "__main__":
    db.init_app(app)
    app.run(port=5000, debug=True)
