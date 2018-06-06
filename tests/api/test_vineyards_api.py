import json
from app import db
from app.models import User, Role, Vineyard, Sensor
from .test_base_api import BaseAPITestCase


class VineyardsAPITestCase(BaseAPITestCase):
    def test_404(self):
        response = self.client.get(
            '/api/v1/vineyards/100',
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
        v1 = Vineyard(name='foo', user_id=self.admin_user.id)
        v2 = Vineyard(name='bar', user_id=self.admin_user.id)
        db.session.add(v1)
        db.session.add(v2)
        db.session.commit()

        response = self.client.get(
            '/api/v1/vineyards/',
            headers=self.get_admin_headers())
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
            data=json.dumps({'name': 'foo'}))

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
