from sqlalchemy import Column, Integer, String, Float
from datetime import date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import MetaData

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)
class BaseModelMixin:

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def simple_filter(cls, **kwargs):
        return cls.query.filter_by(**kwargs).all()



#Modelos
class User(db.Model, BaseModelMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    password = db.Column(db.String(80))
    rol_id = db.Column(db.Integer, db.ForeignKey('rol.id'))
    rol = db.relationship("Rol")

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return f'User({self.username} {self.email})'

    def __str__(self):
        return f'{self.username} {self.email}'


class UserProfile(db.Model, BaseModelMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre = db.Column(db.String(30))
    apellido = db.Column(db.String(30))
    direccion = db.Column(db.String(50))
    ciudad = db.Column(db.String(50))
    telefono= db.Column(db.String(30))
    user = db.relationship("User")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, nombre):
        self.nombre = nombre

    def __repr__(self):
        return f'Datos Personales ({self.nombre} )'

    def __str__(self):
        return f'{self.nombre} {self.apellido}'


class Rol(db.Model, BaseModelMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(unique=True)
    descripcion: Mapped[str]

    def __init__(self, nombre, descripcion):
        self.nombre = nombre
        self.descripcion = descripcion

    def __repr__(self):
        return f'Rol ({self.nombre} {self.descripcion})'

    def __str__(self):
        return f'{self.nombre} {self.nombre}'


class Permiso(db.Model, BaseModelMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(unique=True)
    descripcion: Mapped[str]
    recurso: Mapped[str]
    acceso: Mapped[str]

    def __repr__(self):
        return f'Rol ({self.nombre} {self.descripcion})'

    def __str__(self):
        return f'{self.nombre} {self.nombre}'

class RolPermiso(db.Model):
    id         = db.Column(Integer, primary_key=True)
    rol_id     = db.Column(db.Integer, db.ForeignKey('rol.id'))
    permiso_id = db.Column(db.Integer, db.ForeignKey('permiso.id'))

    def __init__(self, rol_id, permiso_id):
        self.rol_id = rol_id
        self.permiso_id = permiso_id

    def __repr__(self):
        return f'Rol ({self.rol_id}) - Permiso ({self.permiso_id})'




#MODELOS DE LA APLICACION
class WalletContract(db.Model,BaseModelMixin):
    id          = db.Column(Integer, primary_key=True)
    address     = db.Column(db.String(50),nullable=False)
    chain_id    = db.Column(db.Integer(),nullable=False)
    reserved    = db.Column(db.Boolean())

    def __str__(self):
        return self.address


class Wallet(db.Model,BaseModelMixin):
    id              = db.Column(Integer, primary_key=True)
    balance         = db.Column(db.Integer(),nullable=False)
    address         = db.Column(db.String(50),nullable=False)
    coin            = db.Column(db.String(5),nullable=False)
    chain_id        = db.Column(db.Integer(),nullable=False)
    transactions    = db.Column(db.String(10),nullable=False)
    wallet_contract_id = db.Column(db.Integer, db.ForeignKey('wallet_contract.id'))
    wallet_contract = db.relationship("WalletContract")

    def __str__(self):
        return self.address



class Transaction(db.Model,BaseModelMixin):
    id         = db.Column(Integer, primary_key=True)
    nature     = db.Column(db.Integer(),nullable=False)
    tx_hash    = db.Column(db.String(50),nullable=False)
    amount     = db.Column(db.Float(),nullable=True)
    to         = db.Column(db.String(50),nullable=True)
    confirmations = db.Column(db.Integer(),nullable=True)
    status = db.Column(db.Integer(),nullable=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    wallet = db.relationship("Wallet")
    created_at = db.Column(db.Date, nullable=False)

    def __str__(self):
        return self.tx_hash
