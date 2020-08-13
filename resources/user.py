import sqlite3
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt,
)
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from models.user import UserModel
from blacklist import BLACKLIST


_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help="This field can't be blank"
)
_user_parser.add_argument(
    "password", type=str, required=True, help="This field can't be blank"
)


class UserSignup(Resource):
    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return (
                {
                    "status": "fail",
                    "message": f"user: '{data['username']}' already exists",
                },
                400,
            )

        user = UserModel(**data)
        user.save_to_db()

        return (
            {
                "status": "success",
                "message": f"user: '{data['username']}' created successfully",
            },
            201,
        )


class User(Resource):
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"status": "fail", "message": "User not found"}, 404
        return {"status": "success", "user": user.json()}

    @classmethod
    def delete(cls, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"status": "fail", "message": "User not found"}, 404
        try:
            user.delete_from_db()
            print(user.username)
            return {
                "status": "success",
                "message": f"User: '{user.username}' deleted",
            }
        except:
            return {"status": "fail", "message": "A Server error occured"}, 500


class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data["username"])

        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                "status": "success",
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        return {"status": "fail", "message": "Invalid Credentials"}, 401


class UserLogout(Resource):
    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()["jti"]
        BLACKLIST.add(jwt_id)
        return {"message": "logged out"}


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

