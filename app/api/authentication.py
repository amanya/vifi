from flask import g, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, \
    get_jwt_identity, get_jwt_claims, jwt_refresh_token_required, \
    verify_jwt_in_request
from ..models import User
from . import api
from .errors import unauthorized


@api.before_request
def before_request():
    if request.endpoint == 'api.login':
        return
    if request.method == 'OPTIONS':
        return
    verify_jwt_in_request()
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
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

    ret = {
        'jwt': create_access_token(identity=email, fresh=True),
        'refresh_token': create_refresh_token(identity=email)
    }

    return jsonify(ret)

@api.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user.email, fresh=False)
    ret = {
        'access_token': create_access_token(identity=email, fresh=True),
    }

    return jsonify(ret)
