import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, Vineyard, Magnitude, Sensor


class MagnitudeModelTestCase(unittest.TestCase):
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
        m = Magnitude(layer='Surface', type='Temperature', sensor_id=s.id, user_id=u.id)
        db.session.add(m)
        db.session.commit()
        with self.app.test_request_context('/'):
            json_magnitude = m.to_json()
        expected_keys = ['id', 'layer', 'type', 'url', 'user_url', 'sensor_id', 'sensor_url', 'metrics_url', 'created_at']
        self.assertEqual(sorted(json_magnitude.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/magnitudes/' + str(s.id), json_magnitude['url'])
        self.assertEqual('/api/v1/users/' + str(u.id), json_magnitude['user_url'])
        self.assertEqual('/api/v1/magnitudes/' + str(v.id) + '/metrics/',
                         json_magnitude['metrics_url'])
