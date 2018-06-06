from flask import jsonify, g, request,  url_for, current_app
from .. import db
from ..models import Vineyard, Permission, Sensor
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/vineyards/')
def get_vineyards():
    page = request.args.get('page', 1, type=int)
    pagination = Vineyard.query.filter(Vineyard.user_id==g.current_user.id).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    vineyards = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_vineyards', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_vineyards', page=page+1)
    return jsonify({
        'vineyards': [vineyard.to_json() for vineyard in vineyards],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/vineyards/<int:id>')
def get_vineyard(id):
    vineyard = Vineyard.query.get_or_404(id)
    if not (g.current_user.is_administrator() or g.current_user.id == vineyard.user_id):
        return forbidden('Insufficient permissions')
    return jsonify(vineyard.to_json())


@api.route('/vineyards/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_vineyard():
    vineyard = Vineyard.from_json({**request.json, 'user_id': g.current_user.id})
    db.session.add(vineyard)
    db.session.commit()
    return jsonify(vineyard.to_json()), 201, \
        {'Location': url_for('api.get_vineyard', id=vineyard.id)}


@api.route('/vineyards/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_vineyard(id):
    vineyard = Vineyard.query.get_or_404(id)
    vineyard.name = request.json.get('name', vineyard.name)
    db.session.add(vineyard)
    db.session.commit()
    return jsonify(vineyard.to_json())


@api.route('/vineyards/<int:id>/sensors/')
def get_vineyard_sensors(id):
    vineyard = Vineyard.query.filter_by(id=id, user_id=g.current_user.id).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = vineyard.sensors.order_by(Sensor.created_at.desc()).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    sensors = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_vineyard_sensors', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_vineyard_sensors', id=id, page=page+1)
    return jsonify({
        'sensors': [sensor.to_json() for sensor in sensors],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
