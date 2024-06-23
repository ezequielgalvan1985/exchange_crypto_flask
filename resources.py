from flask import request, Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from flask_restful import Api, Resource
from schemas import WalletContractSchema, WalletSchema
from models import Wallet, Permiso, WalletContract
from db import db

walletcontract_serializer = WalletContractSchema()
walletcontract_bp = Blueprint('walletcontract_blueprint', __name__)
api = Api(walletcontract_bp)

class WalletContractListResource(Resource):
    def get(self):
        rows = db.session.execute(db.select(WalletContract).order_by(WalletContract.address)).scalars()
        result = walletcontract_serializer.dump(rows, many=True)
        return result

    #@jwt_required()
    def post(self):
        data = request.get_json()
        record_dict = walletcontract_serializer.load(data)
        m = WalletContract()
        m.address = record_dict['address']
        m.chain_id = record_dict['chain_id']
        m.reserved = record_dict['reserved']
        m.save()
        resp = walletcontract_serializer.dump(m)
        return resp, 201


class WalletContractResource(Resource):
    def get(self, id):
        r = WalletContract.get_by_id(id)
        if r is None:
            return {"mensaje": "registro no existe"}, 404
        resp = walletcontract_serializer.dump(r)
        return resp

    #@jwt_required()
    def delete(self, id):
        r = WalletContract.get_by_id(id)
        if r is None:
            return {"mensaje": "registro no existe"}, 404
        db.session.delete(r)
        db.session.commit()
        return {"mensaje": "registro eliminado"}, 204

    #@jwt_required()
    def put(self, id):
        r = WalletContract.get_by_id(id)
        if r is None:
            return {"message": "No se encontro Id", "data": id}, 404
        data = request.get_json()
        record_dict = walletcontract_serializer.load(data)
        r.address = record_dict['address']
        r.chain_id = record_dict['chain_id']
        r.reserved = record_dict['reserved']
        r.save()
        resp = walletcontract_serializer.dump(r)
        return {"message": "Actualizado Ok", "data": resp}, 200


api.add_resource(WalletContractListResource, '/app-core/v1/wallet-contract',endpoint='walletcontract_list_resource')
api.add_resource(WalletContractResource, '/app-core/v1/wallet-contract/<int:id>', endpoint='walletcontract_resource')

#
#WALLET RESOURCE
#
wallet_serializer = WalletSchema()
wallet_bp = Blueprint('wallet_blueprint', __name__)
api = Api(wallet_bp)

class WalletListResource(Resource):
    def get(self):
        rows = db.session.execute(db.select(WalletContract).order_by(WalletContract.address)).scalars()
        result = walletcontract_serializer.dump(rows, many=True)
        return result

    #@jwt_required()
    def post(self):
        data = request.get_json()
        record_dict = walletcontract_serializer.load(data)
        r = WalletContract()
        r.address = record_dict['address']
        r.chain_id = record_dict['chain_id']
        r.balance = record_dict['balance']
        r.coin = record_dict['coin']
        r.transactions = record_dict['transactions']
        r.save()
        resp = walletcontract_serializer.dump(r)
        return resp, 201


class WalletResource(Resource):
    def get(self, id):
        r = Wallet.get_by_id(id)
        if r is None:
            return {"mensaje": "registro no existe"}, 404
        resp = wallet_serializer.dump(r)
        return resp

    #@jwt_required()
    def delete(self, id):
        r = Wallet.get_by_id(id)
        if r is None:
            return {"mensaje": "registro no existe"}, 404
        db.session.delete(r)
        db.session.commit()
        return {"mensaje": "registro eliminado"}, 204

    #@jwt_required()
    def put(self, id):
        r = Wallet.get_by_id(id)
        if r is None:
            return {"message": "No se encontro Id", "data": id}, 404
        data = request.get_json()
        record_dict = wallet_serializer.load(data)
        r.address = record_dict['address']
        r.chain_id = record_dict['chain_id']
        r.balance = record_dict['balance']
        r.coin = record_dict['coin']
        r.transactions = record_dict['transactions']

        r.save()
        resp = walletcontract_serializer.dump(r)
        return {"message": "Actualizado Ok", "data": resp}, 200


api.add_resource(WalletListResource, '/app-core/v1/wallets',endpoint='wallets_list_resource')
api.add_resource(WalletResource, '/app-core/v1/wallets/<int:id>', endpoint='wallets_resource')