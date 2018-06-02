from flask import jsonify, g, request,  url_for, current_app
from .. import db
from ..models import Alert, Permission
from . import api
from .decorators import permission_required


@api.route('/alerts/')
def get_alerts():
    page = request.args.get('page', 1, type=int)
    pagination = Alert.query.filter(Alert.user_id==g.current_user.id).paginate(
        page, per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False)
    alerts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_alerts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_alerts', page=page+1)
    return jsonify({
        'alerts': [alert.to_json() for alert in alerts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/alerts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_alert():
    fields = request.json
    fields['user_id'] = g.current_user.id
    alert = Alert.from_json(fields)
    db.session.add(alert)
    db.session.commit()
    return jsonify(alert.to_json()), 201, \
            {'Location': url_for('api.get_alerts', id=alert.id)}


@api.route('/alerts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def toggle_ack_alert(id):
    alert = Alert.query.filter_by(id=id, user_id=g.current_user.id).first_or_404()
    alert.acknowledged = not alert.acknowledged
    db.session.add(alert)
    db.session.commit()
    return jsonify(alert.to_json())
