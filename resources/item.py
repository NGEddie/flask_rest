from flask_restful import Resource, reqparse

from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    jwt_optional,
    get_jwt_identity,
    fresh_jwt_required,
)
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "price",
        type=float,
        required=True,
        help="This field can't be left blank",
    )
    parser.add_argument(
        "store_id", type=int, required=True, help="Every item needs a store id"
    )

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)

        if item:
            return {"status": "success", "item": item.json()}
        return {"status": "fail", "message": f"item: '{name}' not found"}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return (
                {"status": "fail", "message": f"item '{name}' already exists"},
                400,
            )

        data = Item.parser.parse_args()
        item = ItemModel(name, **data)

        try:
            item.save_to_db()
            return (
                {
                    "status": "success",
                    "item": item.json(),
                    "message": f"item: '{name}' added",
                },
                201,
            )
        except:
            return (
                {
                    "status": "fail",
                    "message": "An error occurred inserting the item",
                },
                500,
            )

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims["is_admin"]:
            return {"status": "fail", "message": "Admin access needed"}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"status": "success", "message": f"item: '{name}' deleted"}
        return {"status": "fail", "message": f"item: '{name}' not found"}

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            try:
                item = ItemModel(name, **data)
                return (
                    {
                        "status": "success",
                        "message": f"item '{name}' created",
                        "item": item.json(),
                    },
                    201,
                )
            except:
                return (
                    {
                        "status": "fail",
                        "message": "An error occurred adding the item to the database",
                    },
                    500,
                )
        else:
            try:
                item.price = data["price"]
                item.save_to_db()
                return (
                    {
                        "status": "success",
                        "message": f"item '{name}' updated",
                        "item": item.json(),
                    },
                    201,
                )
            except:
                return (
                    {
                        "status": "fail",
                        "message": "An error occurred updating the item in the database",
                    },
                    500,
                )


class Items(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        print(items[0])
        if user_id:
            return {"status": "sucess", "items": items}
        return {
            "status": "success",
            "message": "More details available to logged in users",
            "items": [item["name"] for item in items],
        }

