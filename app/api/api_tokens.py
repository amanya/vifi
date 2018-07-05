from flask import jsonify, g, request,  url_for, current_app
from .. import db
from ..models import ApiToken, Permission
from . import api
from .decorators import permission_required


@api.route('/api-tokens/')
@permission_required(Permission.ADMIN)
def get_api_tokens():
    page = request.args.get('page', 1, type=int)
    pagination = ApiToken.query.filter(ApiToken.user_id==g.current_user.id).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    api_tokens = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_api_tokens', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.api_tokens', page=page+1)
    return jsonify({
        'api-tokens': [api_token.to_json() for api_token in api_tokens],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/api-tokens/<int:id>')
@permission_required(Permission.ADMIN)
def get_api_token(id):
    api_token = ApiToken.query.filter_by(id=id, user_id=g.current_user.id).first_or_404()
    return jsonify(api_token.to_json())


@api.route('/api-tokens/', methods=['POST'])
@permission_required(Permission.ADMIN)
def new_api_token():
    if not request.is_json:
        return unauthorized('Invalid data)')
    if not g.current_user.is_administrator:
        return unauthorized('Invalid credentials')
    params = request.get_json()
    description = params.get('description', '')
    token = g.current_user.generate_api_token(description)
    return jsonify(token.to_json()), 201, \
        {'Location': url_for('api.get_api_token', id=token.id)}
