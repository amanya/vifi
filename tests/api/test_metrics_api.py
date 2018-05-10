import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Vineyard, Sensor, Magnitude, Metric
from .test_base_api import BaseAPITestCase


class MetricsAPITestCase(BaseAPITestCase):
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
        response = self.authenticate('john@example.com', 'dog')
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
