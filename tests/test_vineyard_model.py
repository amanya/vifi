import unittest
import time
from datetime import datetime
from app import create_app, db
from app.models import User, Vineyard


class VineyardModelTestCase(unittest.TestCase):
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
        with self.app.test_request_context('/'):
            json_vineyard = v.to_json()
        expected_keys = ['id', 'name', 'url', 'user_url', 'sensors_url', 'created_at']
        self.assertEqual(sorted(json_vineyard.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/vineyards/' + str(v.id), json_vineyard['url'])
        self.assertEqual('/api/v1/users/' + str(u.id), json_vineyard['user_url'])
        self.assertEqual('/api/v1/vineyards/' + str(v.id) + '/sensors/', json_vineyard['sensors_url'])


