from flask import Blueprint, jsonify

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
