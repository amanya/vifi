from flask import jsonify, request,  url_for, current_app
from .. import db
from ..models import Vineyard, Permission, Sensor, Magnitude, Metric
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/metrics/')
def get_metrics():
    page = request.args.get('page', 1, type=int)
    pagination = Metric.query.paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    metrics = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_metrics', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_metrics', page=page+1)
    return jsonify({
        'metrics': [metric.to_json() for metric in metrics],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/metrics/<int:id>')
def get_metric(id):
    metric = Metric.query.get_or_404(id)
    return jsonify(metric.to_json())


@api.route('/metrics/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_metric():
    metric = Metric.from_json(request.json)
    db.session.add(metric)
    db.session.commit()
    return jsonify(metric.to_json()), 201, \
        {'Location': url_for('api.get_metric', id=metric.id)}
