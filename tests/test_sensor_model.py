import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, Vineyard, Sensor


class SensorModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_to_json(self):
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        v = Vineyard(name='foo', user_id=u.id)
        db.session.add(v)
        db.session.commit()
        s = Sensor(description='foo', latitude=2.4, longitude=1.2, gateway='bar', power_perc=100,
                   vineyard_id=v.id, user_id=u.id)
        db.session.add(s)
        db.session.commit()
        with self.app.test_request_context('/'):
            json_sensor = s.to_json()
        expected_keys = ['id', 'description', 'latitude', 'longitude', 'gateway', 'power_perc',
                         'url', 'user_url', 'vineyard_url', 'magnitudes_url', 'created_at']
        self.assertEqual(sorted(json_sensor.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/sensors/' + str(s.id), json_sensor['url'])
        self.assertEqual('/api/v1/users/' + str(u.id), json_sensor['user_url'])
        self.assertEqual('/api/v1/vineyards/' + str(v.id), json_sensor['vineyard_url'])
        self.assertEqual('/api/v1/sensors/' + str(v.id) + '/magnitudes/',
                         json_sensor['magnitudes_url'])
