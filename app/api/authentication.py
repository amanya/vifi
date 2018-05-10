from flask import g, jsonify, request
from flask_jwt_simple import create_jwt, get_jwt_identity, jwt_required
from ..models import User
from . import api
from .errors import unauthorized, forbidden


@api.before_request
@jwt_required
def before_request():
    if request.endpoint == 'api.login':
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
