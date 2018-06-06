from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, send_from_directory
from flask_login import login_required, current_user
from flask_sqlalchemy import get_debug_queries
from . import main
from .. import db
from ..models import Permission, Role, User
from ..decorators import admin_required, permission_required
import os


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/')
def index():
    return render_template('index.html')

@main.route('/favicon.ico')
def favicon():
    print(main.root_path)
    return send_from_directory(os.path.join(main.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')
