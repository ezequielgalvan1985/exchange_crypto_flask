from marshmallow import fields
from extensiones import ma

class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String()
    email = fields.String()
    password = fields.String()
    rol_id = fields.Integer()
class UserSchemaDto(ma.Schema):
    id = fields.Integer(dump_only=False)
    username = fields.String()


class UserProfileSchema(ma.Schema):
    id = fields.Integer(dump_only=False)
    nombre = fields.String()
    apellido = fields.String()
    direccion = fields.String()
    ciudad = fields.String()
    telefono = fields.String()
    user = ma.Nested(UserSchemaDto, many=False)


class PermisoSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    nombre = fields.String()
    descripcion = fields.String()
    recurso = fields.String()
    acceso = fields.String()



class RolSchema(ma.Schema):
    id = fields.Integer(dump_only=False)
    nombre = fields.String()
    descripcion = fields.String()


class RolPermisoSchema(ma.Schema):
    id = fields.Integer(dump_only=False)
    rol_id = fields.Integer()
    permiso_id = fields.Integer()


class WalletContractSchema(ma.Schema):
    id           = fields.Integer(dump_only=False)
    address      = fields.String()
    chain_id     = fields.Integer()
    reserved     = fields.Boolean()


class WalletSchema(ma.Schema):
    id              = fields.Integer(dump_only=False)
    address         = fields.String()
    chain_id        = fields.Integer()
    balance         = fields.Integer()
    coin            = fields.String()
    transactions    = fields.String()
    wallet_contract = ma.Nested(WalletContractSchema, many=False)

class WalletCreateDtoSchema(ma.Schema):
    user_id         = fields.String()
    chain_id        = fields.String()
    coin            = fields.String()

