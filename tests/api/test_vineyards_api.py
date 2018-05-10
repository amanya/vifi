import unittest
import json
import re
from base64 import b64encode
from app import create_app, db
from app.models import User, Role, Vineyard, Sensor


class VineyardsAPITestCase(unittest.TestCase):
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
                '/auth/login',
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

    def test_404(self):
        response = self.client.get(
            '/api/v1/vineyards/1',
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')

    def test_no_auth(self):
        response = self.client.get('/api/v1/vineyards/',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        # authenticate with bad password
        response = self.authenticate('john@example.com', 'dog')
        self.assertEqual(response.status_code, 401)

    def test_get_vineyards(self):
        v1 = Vineyard(name='foo', user_id=self.writer_user.id)
        v2 = Vineyard(name='bar', user_id=self.writer_user.id)
        db.session.add(v1)
        db.session.add(v2)
        db.session.commit()

        response = self.client.get(
            '/api/v1/vineyards/',
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('count'), 2)
        self.assertEqual(len(json_response.get('vineyards')), 2)

    def test_get_vineyard(self):
        v = Vineyard(name='foo', user_id=self.writer_user.id)
        db.session.add(v)
        db.session.commit()

        response = self.client.get(
            '/api/v1/vineyards/%d' % v.id,
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('id'), v.id)

    def test_cant_get_others_vineyard(self):
        v = Vineyard(name='foo', user_id=self.writer_user.id)
        db.session.add(v)
        db.session.commit()

        response = self.client.get(
            '/api/v1/vineyards/%d' % v.id,
            headers=self.get_reader_headers())
        self.assertEqual(response.status_code, 403)

    def test_admin_can_get_others_vineyard(self):
        v = Vineyard(name='foo', user_id=self.writer_user.id)
        db.session.add(v)
        db.session.commit()

        response = self.client.get(
            '/api/v1/vineyards/%d' % v.id,
            headers=self.get_admin_headers())
        self.assertEqual(response.status_code, 200)

    def test_reader_cant_create_new_vineyard(self):
        response = self.client.post(
            '/api/v1/vineyards/',
            headers=self.get_reader_headers(),
            data=json.dumps({'name': 'foo', 'user_id': self.reader_user.id}))

        self.assertEqual(response.status_code, 403)

    def test_new_vineyard(self):
        response = self.client.post(
            '/api/v1/vineyards/',
            headers=self.get_writer_headers(),
            data=json.dumps({'name': 'foo', 'user_id': self.writer_user.id}))

        self.assertEqual(response.status_code, 201)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['name'], 'foo')

    def test_edit_vineyard(self):
        v = Vineyard(name='foo', user_id=self.writer_user.id)
        db.session.add(v)
        db.session.commit()

        response = self.client.put(
            '/api/v1/vineyards/%d' % v.id,
            headers=self.get_writer_headers(),
            data=json.dumps({'name': 'bar'}))

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['name'], 'bar')

        response = self.client.get(
            '/api/v1/vineyards/%d' % v.id,
            headers=self.get_writer_headers())
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['name'], 'bar')

    def test_vineyard_sensors(self):
        v = Vineyard(name='foo', user_id=self.writer_user.id)
        db.session.add(v)
        db.session.commit()
        s = Sensor(description='bar', latitude=0, longitude=0, gateway='asd',
                   power_perc=0, vineyard_id=v.id, user_id=self.writer_user.id)
        db.session.add(s)
        db.session.commit()

        response = self.client.get(
            '/api/v1/vineyards/%d/sensors/' % v.id,
            headers=self.get_writer_headers())

        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['count'], 1)
        self.assertEqual(json_response['sensors'][0]['id'], s.id)
