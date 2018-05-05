import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Vineyard, Sensor, Magnitude, Metric


class MetricsAPITestCase(unittest.TestCase):
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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, email, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_admin_headers(self):
        return self.get_api_headers('admin@example.com', 'pass')

    def get_reader_headers(self):
        return self.get_api_headers('reader@example.com', 'dog')

    def get_writer_headers(self):
        return self.get_api_headers('john@example.com', 'cat')

    def test_404(self):
        response = self.client.get(
            '/api/v1/metrics/1',
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')

    def test_no_auth(self):
        response = self.client.get('/api/v1/metrics/',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        # authenticate with bad password
        response = self.client.get(
            '/api/v1/metrics/',
            headers=self.get_api_headers('john@example.com', 'dog'))
        self.assertEqual(response.status_code, 401)

    def test_get_metrics(self):
        me1 = Metric(value=10, magnitude_id=self.magnitude.id)
        me2 = Metric(value=20, magnitude_id=self.magnitude.id)
        db.session.add(me1)
        db.session.add(me2)
        db.session.commit()

        response = self.client.get(
            '/api/v1/metrics/',
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('count'), 2)
        self.assertEqual(len(json_response.get('metrics')), 2)

    def test_reader_cant_create_new_metrics(self):
        response = self.client.post(
            '/api/v1/metrics/',
            headers=self.get_reader_headers(),
            data=json.dumps({'value': 10, 'magnitude_id': self.magnitude.id}))

        self.assertEqual(response.status_code, 403)

    def test_new_metric(self):
        response = self.client.post(
            '/api/v1/metrics/',
            headers=self.get_writer_headers(),
            data=json.dumps({'value': 10.0, 'magnitude_id': self.magnitude.id}))

        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['value'], '10.0')
