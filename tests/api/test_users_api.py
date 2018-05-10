import json
from app import db
from app.models import User, Role
from .test_base_api import BaseAPITestCase


class UsersAPITestCase(BaseAPITestCase):
    def test_404(self):
        response = self.client.get(
            '/wrong/url',
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')

    def test_no_auth(self):
        response = self.client.get('/api/v1/users',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_bad_auth(self):
        # authenticate with bad password
        response = self.authenticate('john@example.com', 'dog')
        self.assertEqual(response.status_code, 401)

    def test_anonymous(self):
        response = self.client.get(
            '/api/v1/users')
        self.assertEqual(response.status_code, 401)

    def test_unconfirmed_account(self):
        # add an unconfirmed user
        r = Role.query.filter_by(name='Reader').first()
        self.assertIsNotNone(r)
        u = User(email='ada@example.com', password='cat', confirmed=False,
                 role=r)
        db.session.add(u)
        db.session.commit()

        # can't get list of items with the unconfirmed account
        response = self.client.get(
            '/api/v1/vineyard/',
            headers=self.get_api_headers('ada@example.com', 'cat'))
        self.assertEqual(response.status_code, 404)

    def test_admin_user(self):
        # admin user can read non-admin user info
        response = self.client.get(
            '/api/v1/users/%d' % self.writer_user.id,
            headers=self.get_api_headers('admin@example.com', 'pass'))
        self.assertEqual(response.status_code, 200)

        # non-admin get unauthorized when accesing other user info
        response = self.client.get(
            '/api/v1/users/%d' % self.admin_user.id,
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 403)

        # non-admin can read their own data
        response = self.client.get(
            '/api/v1/users/%d' % self.writer_user.id,
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 200)

    def test_get_logged_in_user(self):
        # user can read their own info
        response = self.client.get(
            '/api/v1/users',
            headers=self.get_api_headers('john@example.com', 'cat'))
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response.get('id'), self.writer_user.id)
