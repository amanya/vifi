import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Vineyard, Sensor, Magnitude


class BaseAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

        # add regular user
        r = Role.query.filter_by(name='Writer').first()
        u = User(email='john@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()
        self.writer_user = u

        # add a vineyard for the regular user
        v = Vineyard(name='foo', user_id=self.writer_user.id)
        db.session.add(v)
        db.session.commit()
        self.vineyard = v

        # add a sensor for the regular user
        s = Sensor(description='bar', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.writer_user.id)
        db.session.add(s)
        db.session.commit()
        self.sensor = s

        # add a magnitude for the regular user
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()
        self.magnitude = m

        # add a read only user
        r = Role.query.filter_by(name='Reader').first()
        u = User(email='reader@example.com', password='dog', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()
        self.reader_user = u

        # add an admin user
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='admin@example.com', password='pass', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()
        self.admin_user = u

        self.tokens = {}

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def authenticate(self, email, password):
        headers = {'Accept': 'application/json',
                    'Content-Type': 'application/json'}
        data = {'username': email, 'password': password}

        return self.client.post(
                '/api/v1/login',
                headers=headers,
                data=json.dumps(data))

    def get_api_headers(self, email, password):
        if not email in self.tokens:
            response = self.authenticate(email, password)
            json_response = json.loads(response.get_data(as_text=True))
            self.tokens[email] = json_response['jwt']

        headers = { 'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + self.tokens[email]}
        return headers

    def get_admin_headers(self):
        return self.get_api_headers('admin@example.com', 'pass')

    def get_reader_headers(self):
        return self.get_api_headers('reader@example.com', 'dog')

    def get_writer_headers(self):
        return self.get_api_headers('john@example.com', 'cat')

 
