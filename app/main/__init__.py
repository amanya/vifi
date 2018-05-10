from flask import Blueprint, jsonify, request
from flask_jwt_simple import create_jwt

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission, User


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/login', methods=['POST'])
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
