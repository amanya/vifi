from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import JSONWebSignatureSerializer, TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from flask_login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from sqlalchemy import Index, desc
from . import db


class Permission:
    READ = 1
    WRITE = 2
    ADMIN = 4 

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    acknowledged = db.Column(db.Boolean, nullable=False)
    priority = db.Column(db.Enum('Info', 'Warning', 'Danger'))
    origin = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(), onupdate=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    def to_json(self):
        json_alert = {
            'id': self.id,
            'acknowledged': self.acknowledged,
            'content': self.content,
            'priority': self.priority,
            'origin': self.origin,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'user_id': self.user_id,
        }
        return json_alert

    @staticmethod
    def from_json(json_alert):
        content = json_alert.get('content', None)
        if content is None:
            raise ValidationError('alert does not have a content')
        user_id = json_alert.get('user_id', None)
        if user_id is None:
            raise ValidationError('alert does not have a user_id')
        priority = json_alert.get('priority', None)
        if priority is None:
            raise ValidationError('alert does not have a priority')
        origin = json_alert.get('origin', None)
        return Alert(content=content, user_id=user_id, priority=priority, origin=origin,
                acknowledged=False)

    def __repr__(self):
        return '<Alert (%r)>' % self.content


class Metric(db.Model):
    __tablename__ = 'metrics'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    value = db.Column(db.Float, nullable=False)
    magnitude_id = db.Column(db.Integer, db.ForeignKey('magnitudes.id'), nullable=False, index=True)

    def to_json(self):
        json_metric = {
            'id': self.id,
            'timestamp': self.timestamp,
            'value': str(self.value),
            'magnitude_url': url_for('api.get_magnitude', id=self.magnitude_id)
        }
        return json_metric

    @staticmethod
    def from_json(json_metric):
        timestamp = json_metric.get('timestamp', None)
        value = json_metric.get('value')
        if value is None:
            raise ValidationError('metric does not have a value')
        magnitude_id = json_metric.get('magnitude_id')
        if magnitude_id is None:
            raise ValidationError('metric does not have a magnitude_id')
        return Metric(timestamp=timestamp, value=value, magnitude_id=magnitude_id)

    def __repr__(self):
        return '<Metric (%r, %r)>' % (self.timestamp, self.value)


class Magnitude(db.Model):
    __tablename__ = 'magnitudes'
    id = db.Column(db.Integer, primary_key=True)
    layer = db.Column(db.Enum('Surface', 'Depth 1', 'Depth 2'), nullable=False, index=True)
    type = db.Column(db.Enum('Temperature', 'Humidity', 'Conductivity', 'pH', 'Light', 'Dew'), nullable=False, index=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)
    metrics = db.relationship('Metric', backref='magnitude', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    Index('idx_user_layer_type', user_id, layer, type)

    def to_json(self):
        json_magnitude = {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'layer': self.layer,
            'type': self.type,
            'url': url_for('api.get_magnitude', id=self.id),
            'user_url': url_for('api.get_user', id=self.user_id),
            'sensor_url': url_for('api.get_sensor', id=self.sensor_id),
            'metrics_url': url_for('api.get_magnitude_metrics', id=self.id),
            'created_at': self.created_at
        }
        return json_magnitude

    @staticmethod
    def from_json(json_magnitude):
        layer = json_magnitude.get('layer')
        if layer is None:
            raise ValidationError('magnitude does not have a layer')
        type = json_magnitude.get('type')
        if type is None:
            raise ValidationError('magnitude does not have a type')
        sensor_id = json_magnitude.get('sensor_id')
        if sensor_id is None:
            raise ValidationError('magnitude does not have a sensor_id')
        user_id = json_magnitude.get('user_id')
        if user_id is None:
            raise ValidationError('magnitude does not have a user_id')
        return Magnitude(layer=layer, type=type, sensor_id=sensor_id, user_id=user_id)

    def __repr__(self):
        return '<Magnitude (%r - %r)>' % (self.layer, self.type)


class Sensor(db.Model):
    __tablename__ = 'sensors'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    gateway = db.Column(db.String(256))
    power_perc = db.Column(db.Float)
    magnitudes = db.relationship('Magnitude', backref='sensor', lazy='dynamic')
    vineyard_id = db.Column(db.Integer, db.ForeignKey('vineyards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def last_metrics(self):
        ret = []
        for magnitude in self.magnitudes:
            last_metric = magnitude.metrics.order_by(desc(Metric.timestamp)).limit(1).first()
            ret.append({
                'magnitude_id': magnitude.id,
                'timestamp': last_metric.timestamp,
                'value': last_metric.value
            })
        return ret

    def to_json(self):
        magnitudes_json = [m.to_json() for m in self.magnitudes.all()]
        json_sensor = {
            'id': self.id,
            'description': self.description,
            'latitude': str(self.latitude),
            'longitude': str(self.longitude),
            'gateway': str(self.gateway),
            'power_perc': str(self.power_perc),
            'magnitudes': magnitudes_json,
            'url': url_for('api.get_sensor', id=self.id),
            'user_url': url_for('api.get_user', id=self.user_id),
            'vineyard_url': url_for('api.get_vineyard', id=self.vineyard_id),
            'magnitudes_url': url_for('api.get_sensor_magnitudes', id=self.id),
            'created_at': self.created_at
        }
        return json_sensor

    @staticmethod
    def from_json(json_sensor):
        description = json_sensor.get('description')
        if description is None:
            raise ValidationError('sensor does not have a description')
        latitude = json_sensor.get('latitude')
        if latitude is None:
            raise ValidationError('sensor does not have a latitude')
        longitude = json_sensor.get('longitude')
        if longitude is None:
            raise ValidationError('sensor does not have a longitude')
        gateway = json_sensor.get('gateway')
        if gateway is None:
            raise ValidationError('sensor does not have a gateway')
        power_perc = json_sensor.get('power_perc')
        if power_perc is None:
            raise ValidationError('sensor does not have a power_perc')
        vineyard_id = json_sensor.get('vineyard_id')
        if vineyard_id is None:
            raise ValidationError('sensor does not have a vineyard_id')
        user_id = json_sensor.get('user_id')
        if user_id is None:
            raise ValidationError('sensor does not have a user_id')
        return Sensor(description=description,
                      latitude=latitude,
                      longitude=longitude,
                      gateway=gateway,
                      power_perc=power_perc,
                      vineyard_id=vineyard_id,
                      user_id=user_id)


class Vineyard(db.Model):
    __tablename__ = 'vineyards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    sensors = db.relationship('Sensor', backref='vineyard', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        json_vineyard = {
            'id': self.id,
            'name': self.name,
            'sensors': [s.to_json() for s in self.sensors.all()],
            'url': url_for('api.get_vineyard', id=self.id),
            'user_url': url_for('api.get_user', id=self.user_id),
            'sensors_url': url_for('api.get_vineyard_sensors', id=self.id),
            'created_at': self.created_at
        }
        return json_vineyard

    @staticmethod
    def from_json(json_vineyard):
        name = json_vineyard.get('name')
        if name is None:
            raise ValidationError('vineyard does not have a name')
        user_id = json_vineyard.get('user_id')
        if user_id is None:
            raise ValidationError('vineyard does not have a user_id')
        return Vineyard(name=name, user_id=user_id)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'Reader': [Permission.READ],
            'Writer': [Permission.READ, Permission.WRITE],
            'Administrator': [Permission.READ, Permission.WRITE,
                              Permission.ADMIN],
        }
        default_role = 'Reader'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


class ApiToken(db.Model):
    __tablename__ = 'api_tokens'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    enabled = db.Column(db.Boolean, default=True)

    @property
    def token(self):
        s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'id': self.user_id, 'timestamp': str(self.timestamp)}).decode('utf-8')

    def to_json(self):
        json_api_token = {
            'id': self.id,
            'description': self.description,
            'token': self.token,
            'timestamp': self.timestamp,
            'url': url_for('api.get_api_token', id=self.id),
        }
        return json_api_token

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    vineyards = db.relationship('Vineyard', backref='client', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def to_json(self):
        json_user = {
            'id': self.id,
            'email': self.email,
            'admin': self.is_administrator(),
            'url': url_for('api.get_user', id=self.id),
            'vineyards_url': url_for('api.get_user_vineyards', id=self.id),
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    def generate_api_token(self, description):
        timestamp = datetime.utcnow()
        api_token = ApiToken(user_id=self.id, timestamp=timestamp, description=description)
        db.session.add(api_token)
        db.session.commit()
        return api_token

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.email


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

