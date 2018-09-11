import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Vineyard, Sensor, Magnitude, Metric
from .test_base_api import BaseAPITestCase


class MagnitudesAPITestCase(BaseAPITestCase):
    def test_404(self):
        response = self.client.get(
            '/api/v1/magnitudes/100',
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
        response = self.authenticate('john@example.com', 'dog')
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
        self.assertEqual(json_response.get('count'), 3)
        self.assertEqual(len(json_response.get('magnitudes')), 3)

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

    def test_delete_magnitude(self):
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=self.writer_user.id)
        db.session.add(m)
        db.session.commit()

        response = self.client.delete(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_writer_headers())

        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 404)

    def test_cant_delete_magnitude(self):
        r = Role.query.filter_by(name='Writer').first()
        u = User(email='jack@example.com', password='cat', confirmed=True,
                 role=r)
        db.session.add(u)
        db.session.commit()

        m = Magnitude(layer='Surface', type='Temperature', sensor_id=self.sensor.id,
                      user_id=u.id)
        db.session.add(m)
        db.session.commit()

        response = self.client.delete(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_writer_headers())

        self.assertEqual(response.status_code, 403)

        response = self.client.get(
            '/api/v1/magnitudes/%d' % m.id,
            headers=self.get_api_headers('jack@example.com', 'cat'))
        self.assertEqual(response.status_code, 200)

    def test_magnitude_metrics(self):
        me = Metric(value=10, magnitude_id=self.magnitude.id)
        db.session.add(me)
        db.session.commit()

        response = self.client.get(
            '/api/v1/magnitudes/%d/metrics/' % self.magnitude.id,
            headers=self.get_writer_headers())

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['count'], 1)
        self.assertEqual(json_response['metrics'][0]['id'], me.id)
