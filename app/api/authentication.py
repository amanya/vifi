from flask import g, jsonify, request
from flask_jwt_simple import create_jwt, get_jwt_identity, jwt_optional
from ..models import User
from . import api
from .errors import unauthorized, forbidden


@api.before_request
@jwt_optional
def before_request():
    if request.endpoint == 'api.login':
        return
    if request.method == 'OPTIONS':
        return
    user = User.query.filter_by(email=get_jwt_identity()).first()
    if not user:
        return unauthorized('Invalid credentials')
    g.current_user = user
    g.token_used = True


@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})


@api.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return unauthorized('Invalid credentials)')

    params = request.get_json()
    email = params.get('username', None)
    password = params.get('password', None)

    if not email or not password:
        return unauthorized('Invalid credentials')

    user = User.query.filter_by(email=email).first()
    if not user:
        return unauthorized('Invalid credentials')

    if not user.verify_password(password):
        return unauthorized('Invalid credentials')

    ret = {'jwt': create_jwt(identity=email)}

    return jsonify(ret)
