import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Vineyard, Sensor, Magnitude, Metric


class MagnitudesAPITestCase(unittest.TestCase):
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
            '/api/v1/magnitudes/1',
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')

    def test_no_auth(self):
        response = self.client.get('/api/v1/magnitudes/',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        # authenticate with bad password
        response = self.client.get(
            '/api/v1/magnitudes/',
            headers=self.get_api_headers('john@example.com', 'dog'))
        self.assertEqual(response.status_code, 401)

    def test_get_magnitudes(self):
        m1 = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                       user_id=self.writer_user.id)
        m2 = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                       user_id=self.writer_user.id)
        db.session.add(m1)
        db.session.add(m2)
        db.session.commit()

        response = self.client.get(
            '/api/v1/magnitudes/',
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('count'), 2)
        self.assertEqual(len(json_response.get('magnitudes')), 2)

    def test_get_magnitude(self):
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()

        response = self.client.get(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('id'), m.id)

    def test_cant_get_others_magnitude(self):
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()

        response = self.client.get(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_reader_headers())
        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_others_magnitude(self):
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()

        response = self.client.get(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200)

    def test_reader_cant_create_new_magnitude(self):
        response = self.client.post(
            '/api/v1/magnitudes/',
            headers=self.get_reader_headers(),
            data=json.dumps({'layer': 'Depth 1', 'type': 'Humidity', 'user_id': self.reader_user.id}))

        self.assertEqual(response.status_code, 403)

    def test_new_magnitude(self):
        response = self.client.post(
            '/api/v1/magnitudes/',
            headers=self.get_writer_headers(),
            data=json.dumps({'layer': 'Depth 1', 'type': 'Humidity',
                             'sensor_id': self.sensor.id, 'user_id': self.writer_user.id}))

        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['layer'], 'Depth 1')

    def test_edit_magnitude(self):
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()

        response = self.client.put(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_writer_headers(),
            data=json.dumps({'layer': 'Depth 1'}))

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['layer'], 'Depth 1')

        response = self.client.get(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['layer'], 'Depth 1')

    def test_magnitude_metrics(self):
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()
        me = Metric(value=10, magnitude_id=m.id)
        db.session.add(me)
        db.session.commit()

        response = self.client.get(
            '/api/v1/magnitudes/%d/metrics/' % me.id,
            headers=self.get_writer_headers())

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['count'], 1)
        self.assertEqual(json_response['metrics'][0]['id'], me.id)
