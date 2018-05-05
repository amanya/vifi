from flask import jsonify, g, request,  url_for, current_app
from .. import db
from ..models import Vineyard, Permission, Sensor, Magnitude
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/sensors/')
def get_sensors():
    page = request.args.get('page', 1, type=int)
    pagination = Sensor.query.filter(Sensor.user_id==g.current_user.id).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    sensors = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_sensors', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_sensors', page=page+1)
    return jsonify({
        'sensors': [sensor.to_json() for sensor in sensors],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/sensors/<int:id>')
def get_sensor(id):
    sensor = Sensor.query.get_or_404(id)
    if not (g.current_user.is_administrator() or g.current_user.id == sensor.user_id):
        return forbidden('Insufficient permissions')
    return jsonify(sensor.to_json())


@api.route('/sensors/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_sensor():
    sensor = Sensor.from_json(request.json)
    db.session.add(sensor)
    db.session.commit()
    return jsonify(sensor.to_json()), 201, \
        {'Location': url_for('api.get_sensor', id=sensor.id)}


@api.route('/sensors/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_sensor(id):
    sensor = Sensor.query.filter_by(id=id, user_id=g.current_user.id).first_or_404()
    sensor.description = request.json.get('description', sensor.description)
    db.session.add(sensor)
    db.session.commit()
    return jsonify(sensor.to_json())


@api.route('/sensors/<int:id>/magnitudes/')
def get_sensor_magnitudes(id):
    sensor = Sensor.query.filter_by(id=id, user_id=g.current_user.id).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = sensor.magnitudes.order_by(Magnitude.created_at.desc()).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    magnitudes = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_sensor_magnitudes', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_sensor_magnitudes', id=id, page=page+1)
    return jsonify({
        'magnitudes': [magnitude.to_json() for magnitude in magnitudes],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
