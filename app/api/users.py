from flask import jsonify, g, request, current_app, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from .errors import forbidden
from ..models import User, Vineyard

@api.route('/users')
def get_users():
    user = User.query.get_or_404(g.current_user.id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>')
def get_user(id):
    if not (g.current_user.is_administrator() or g.current_user.id == id):
        return forbidden('Insufficient permissions')
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/vineyards')
def get_user_vineyards(id):
    if not (g.current_user.is_administrator() or g.current_user.id == id):
        return forbidden('Insufficient permissions')
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.vineyards.order_by(Vineyard.created_at.desc()).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    vineyards = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_vineyards', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_vineyards', id=id, page=page+1)
    return jsonify({
        'vineyards': [vineyard.to_json() for vineyard in vineyards],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
