from flask import request, Blueprint, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from flask_restful import Api, Resource
from schemas import WalletContractSchema, WalletSchema, WalletCreateDtoSchema, WalletWithdrawDtoSchema
from models import Wallet, Permiso, WalletContract
from db import db
from services import WalletService

#serializers
walletcontract_serializer = WalletContractSchema()
wallet_serializer = WalletSchema()

controllers_blueprint = Blueprint('controllers_blueprint', __name__)
api = Api(controllers_blueprint)

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

class WalletListResource(Resource):
    _serializer= None
    _createDto = None
    def __init__(self):
        self._serializer = WalletSchema()
        self._createDto = WalletCreateDtoSchema()
    def get(self):
        rows = db.session.execute(db.select(Wallet).order_by(Wallet.address)).scalars()
        result = self._serializer.dump(rows, many=True)
        return result

    #@jwt_required()
    def post(self):
        try:
            d = request.get_json()
            print(d)
            #recibir dto coin, chain_id, user_id
            #_createDto = WalletCreateDtoSchema()
            d = self._createDto.load(d)
            #buscar una wallet contract libre para el chain_id
            c = WalletContract.query.filter_by(reserved=False,
                                               chain_id=d['chain_id']).first()
            if c is None:
                return {"message":"No existe Contratos disponibles"},400
            #verificar si no existe wallet por address, chain_id y coin
            w = Wallet.query.filter_by(chain_id=d['chain_id'],
                                       address=c.address,
                                       coin=d['coin']).first()

            if w is None:
                w = Wallet()
                w.balance = 0
                w.coin = d['coin']
                w.chain_id = d['chain_id']
                w.address = c.address
                w.wallet_contract = c
                w.transactions = ''
                w.save()

                c.reserved = True
                c.save()
                response = self._serializer.dump(w)
                return response, 201
            return {"message": "Contrato ya esta asignado a una Wallet"}, 400

        except Exception as e:
            return {"message":e},500

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

#-----------------------------
#Otras funciones
#-----------------------------

class WalletWithdraw(Resource):
    def __init__(self):
        self._serializer = WalletWithdrawDtoSchema()
    def post(self):
        try:
            data = request.get_json()
            record_dict = self._serializer.load(data)
            s = WalletService()
            s.send_withdraw_queue(data)
            return data, 200
        except Exception as e:
            return {"message": e}, 500

api.add_resource(WalletWithdraw, '/app-core/v1/wallets/withdraw', endpoint='wallets_withdraw_resource')
