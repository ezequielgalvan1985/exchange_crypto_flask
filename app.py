from datetime import timedelta
from flask import request, jsonify
from flask_restful import Api, abort
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from werkzeug.security import check_password_hash

from extensiones import ma, migrate
from models import User, RolPermiso, UserProfile
from db import db
from resources import wallet_bp, walletcontract_bp
from schemas import UserSchemaDto, RolPermisoSchema, UserSchema, UserProfileSchema
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, current_user, \
    get_jwt, create_refresh_token
from flask_jwt_extended import jwt_required
from flask_cors import CORS, cross_origin


user_serializer = UserSchema()
userprofile_serializer = UserProfileSchema()


#variables globales
SECRET_KEY = '123447a47f563e90fe2db0f56b1b17be62378e31b7cfd3adc776c59ca4c75e2fc512c15f69bb38307d11d5d17a41a7936789'
PROPAGATE_EXCEPTIONS = True
# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///project.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SHOW_SQLALCHEMY_LOG_MESSAGES = False
ERROR_404_HELP = False

#configuracion
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8100", "http://127.0.0.1:8100"]}})

#app.config['CORS_HEADERS'] = 'Content-Type'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PROPAGATE_EXCEPTIONS'] = PROPAGATE_EXCEPTIONS
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SHOW_SQLALCHEMY_LOG_MESSAGES'] = SHOW_SQLALCHEMY_LOG_MESSAGES
app.config['ERROR_404_HELP'] = ERROR_404_HELP
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1)

jwt = JWTManager(app)


#urls de pruebas
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

@app.route('/user-profile')
@jwt_required()
def user_profile():
    current_user_id = get_jwt_identity()
    return f'Profile of user {current_user_id}'


@app.errorhandler(401)
def custom_401(error):
    return jsonify({"message": "Token has expired"}), 401

@app.route('/api/v1.0/auth/protected', methods=['GET'])
@jwt_required()
def protected():
    claims = get_jwt()
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user, claims=claims), 200


@app.route('/api/v1.0/auth/login', methods=['POST'])
@cross_origin("http://localhost:8100")
def login():
    data = request.get_json()
    record_dict = user_serializer.load(data)
    user = User.query.filter_by(username=record_dict['username']).first()
    if user is None:
        abort(404, description="No se encontro usuario")
    if not check_password_hash(user.password, record_dict['password']):
        abort(400, "Usuario o contraseña Invalido")
    #setear los permisos
    permisos = RolPermiso.query.filter_by(rol_id=user.rol_id).all()

    rolPermiso_serializer = RolPermisoSchema()
    permisosJson = rolPermiso_serializer.dump(permisos,many=True)

    additional_claims = {"permisos": permisosJson}
    access_token = create_access_token(identity=user, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user, additional_claims=additional_claims)

    return {"access_token":access_token,"refresh_token":refresh_token,"login":user.username, "user_id":user.id},200


@app.route('/api/v1.0/auth/refresh-token', methods=['POST'])
@cross_origin("http://localhost:8100")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    print(identity)
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)



@app.route('/api/v1.0/auth/check-token', methods=['GET'])
@cross_origin("http://localhost:8100")
@jwt_required(refresh=True)
def check_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)

#metodos personalizados
#Consultas Categorias


@app.route("/api/v1.0/datospersonales/consultas/findbyuser/<int:id>", methods=["GET"])
@jwt_required()
def datospersonalesFindByUserId(id):
    u = User.query.filter_by(id=id)
    print("flag1")
    if u is None:
        return {"message":"No existen Usuario"+ id, "code":1}, 400

    r=UserProfile.query.filter_by(user_id=u.id).first()
    if r is None:
        return {"message":"No existen Datos para el Usuario "+ id, "code":1}, 400

    resp = userprofile_serializer.dump(r, many=False)
    return resp, 200

user_dto_serializer = UserSchemaDto()


# Captura todos los errores 404
Api(app, catch_all_404s=True)

db.init_app(app)
ma.init_app(app)
migrate.init_app(app, db)


# Deshabilita el modo estricto de acabado de una URL con /
app.url_map.strict_slashes = False


# Registra los blueprints
app.register_blueprint(walletcontract_bp)
app.register_blueprint(wallet_bp)

#Workers

if __name__ == '__main__':

    app.run(debug=True)
