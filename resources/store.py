from flask_restful import Resource
from models.store import StoreModel


class Store(Resource):
    def get(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            return {'status': 'success', 'store': store.json()}, 200
        return {
            'status': 'fail',
            'message': f'store: \'{name}\' not found'
        }, 404

    def post(self, name):
        if StoreModel.find_by_name(name):
            return {
                'status': 'fail',
                'message': f'Store \'{name}\' already exists'
            }
        try:
            store = StoreModel(name)
            store.save_to_db()
            return {
                'status': 'success',
                'message': f'Store \'{name}\' created'
            }
        except:
            return {
                'status': 'fail',
                'message': 'A Server Error Occurred'
            }, 500

    def delete(self, name):
        store = StoreModel.find_by_name(name)
        if store:
            try:
                store.delete_from_db()
                return {
                    'status': 'success',
                    'message': f'store \'{name}\' deleted'
                }
            except:
                return {'status': 'fail', 'message': ''}


class Stores(Resource):
    def get(self):
        return {'stores': [store.json() for store in StoreModel.find_all()]}
