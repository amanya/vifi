from flask import jsonify, g, request,  url_for, current_app
from .. import db
from ..models import Vineyard, Permission, Sensor, Magnitude, Metric
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/magnitudes/')
def get_magnitudes():
    page = request.args.get('page', 1, type=int)
    pagination = Magnitude.query.filter(Magnitude.user_id==g.current_user.id).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    magnitudes = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_magnitudes', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_magnitudes', page=page+1)
    return jsonify({
        'magnitudes': [magnitude.to_json() for magnitude in magnitudes],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/magnitudes/<int:id>')
def get_magnitude(id):
    magnitude = Magnitude.query.get_or_404(id)
    if not (g.current_user.is_administrator() or g.current_user.id == magnitude.user_id):
        return forbidden('Insufficient permissions')
    return jsonify(magnitude.to_json())


@api.route('/magnitudes/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_magnitude():
    magnitude = Magnitude.from_json(request.json)
    db.session.add(magnitude)
    db.session.commit()
    return jsonify(magnitude.to_json()), 201, \
        {'Location': url_for('api.get_magnitude', id=magnitude.id)}


@api.route('/magnitudes/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_magnitude(id):
    magnitude = Magnitude.query.get_or_404(id)
    magnitude.type = request.json.get('type', magnitude.type)
    magnitude.layer = request.json.get('layer', magnitude.layer)
    magnitude.sensor_id = request.json.get('sensor_id', magnitude.sensor_id)
    db.session.add(magnitude)
    db.session.commit()
    return jsonify(magnitude.to_json())

@api.route('/magnitudes/<int:id>', methods=['DELETE'])
@permission_required(Permission.WRITE)
def delete_magnitude(id):
    magnitude = Magnitude.query.get_or_404(id)
    if not (g.current_user.is_administrator() or g.current_user.id == magnitude.user_id):
        return forbidden('Insufficient permissions')
    Magnitude.query.filter_by(id=id).delete()
    db.session.commit()
    return jsonify(magnitude.to_json())


@api.route('/magnitudes/<int:id>/metrics/')
def get_magnitude_metrics(id):
    magnitude = Magnitude.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = magnitude.metrics.order_by(Metric.timestamp.desc()).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    metrics = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_magnitude_metrics', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_magnitude_metrics', id=id, page=page+1)
    return jsonify({
        'metrics': [metric.to_json() for metric in metrics],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
