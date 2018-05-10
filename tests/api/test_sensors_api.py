import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Vineyard, Sensor, Magnitude
from .test_base_api import BaseAPITestCase


class SensorsAPITestCase(BaseAPITestCase):
    def test_404(self):
        response = self.client.get(
            '/api/v1/sensors/100',
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')

    def test_no_auth(self):
        response = self.client.get('/api/v1/sensors/',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        # authenticate with bad password
        response = self.authenticate('john@example.com', 'dog')
        self.assertEqual(response.status_code, 401)

    def test_get_sensors(self):
        s1 = Sensor(description='foo', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.admin_user.id)
        s2 = Sensor(description='bar', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.admin_user.id)
        db.session.add(s1)
        db.session.add(s2)
        db.session.commit()

        response = self.client.get(
            '/api/v1/sensors/',
            headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('count'), 2)
        self.assertEqual(len(json_response.get('sensors')), 2)

    def test_get_sensor(self):
        s = Sensor(description='foo', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.writer_user.id)
        db.session.add(s)
        db.session.commit()

        response = self.client.get(
            '/api/v1/sensors/%d' % s.id,
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('id'), s.id)

    def test_cant_get_others_sensor(self):
        s = Sensor(description='foo', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.writer_user.id)
        db.session.add(s)
        db.session.commit()

        response = self.client.get(
            '/api/v1/sensors/%d' % s.id,
            headers=self.get_reader_headers())
        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_others_sensor(self):
        s = Sensor(description='foo', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.writer_user.id)
        db.session.add(s)
        db.session.commit()

        response = self.client.get(
            '/api/v1/sensors/%d' % s.id,
            headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200)

    def test_reader_cant_create_new_sensor(self):
        response = self.client.post(
            '/api/v1/sensors/',
            headers=self.get_reader_headers(),
            data=json.dumps({'name': 'foo', 'user_id': self.reader_user.id}))

        self.assertEqual(response.status_code, 403)

    def test_new_sensor(self):
        response = self.client.post(
            '/api/v1/sensors/',
            headers=self.get_writer_headers(),
            data=json.dumps({'description': 'foo',
                             'latitude': 0,
                             'longitude': 0,
                             'gateway': 'asdf',
                             'power_perc': 100,
                             'vineyard_id': self.vineyard.id,
                             'user_id': self.writer_user.id}))

        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['description'], 'foo')

    def test_edit_sensor(self):
        s = Sensor(description='foo', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.writer_user.id)
        db.session.add(s)
        db.session.commit()

        response = self.client.put(
            '/api/v1/sensors/%d' % s.id,
            headers=self.get_writer_headers(),
            data=json.dumps({'description': 'bar'}))

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['description'], 'bar')

        response = self.client.get(
            '/api/v1/sensors/%d' % s.id,
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['description'], 'bar')

    def test_sensor_magnitudes(self):
        s = Sensor(description='foo', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=self.vineyard.id, user_id=self.writer_user.id)
        db.session.add(s)
        db.session.commit()
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=s.id, user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()

        response = self.client.get(
            '/api/v1/sensors/%d/magnitudes/' % s.id,
            headers=self.get_writer_headers())

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['count'], 1)
        self.assertEqual(json_response['magnitudes'][0]['id'], m.id)
