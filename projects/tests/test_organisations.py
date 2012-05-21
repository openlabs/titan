# -*- coding: utf-8 -*-
"""
    test_organisations

    Test the organisations API

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
from urllib import urlencode

from tornado import testing, options
from monstor.app import make_app
from titan.projects.models import User
from titan.settings import SETTINGS


class TestOrganisations(testing.AsyncHTTPTestCase):

    def get_app(self):
        options.options.database = 'test_titan'
        SETTINGS['xsrf_cookies'] = False
        application = make_app(**SETTINGS)
        return application

    def setUp(self):
        super(TestOrganisations, self).setUp()
        user = User(name="Test User", email="test@example.com")
        user.set_password("password")
        user.save()

    def get_login_cookie(self):
        response = self.fetch(
            '/login', method="POST", follow_redirects=False,
            body=urlencode({'email': 'test@example.com', 'password': 'password'})
        )
        return response.headers['Set-Cookie']

    def test_0020_get_applications(self):
        """
        Test the HTML response
        """
        response = self.fetch(
            '/organisations/', method="GET", follow_redirects=False
        )
        self.assertEqual(response.code, 302)

        response = self.fetch(
            '/organisations/', method="GET", follow_redirects=False,
            headers={'Cookie': self.get_login_cookie()}
        )

    def test_0030_get_applications(self):
        """
        Test the JSON response
        """
        response = self.fetch(
            '/organisations/', method="GET", follow_redirects=False,
            headers={'X-Requested-With': 'XMLHTTPRequest'}
        )
        self.assertEqual(response.code, 302)

    def test_0040_get_invalid_organisation(self):
        """
        Try to GET and org which doesnt exist and look for 302 when not logged
        in and a 404 when logged in 
        """
        response = self.fetch(
            '/organisations/an-invalid-org', method="GET", 
            follow_redirects=False,
        )
        self.assertEqual(response.code, 302)

        response = self.fetch(
            '/organisations/an-invalid-org', method="GET", 
            follow_redirects=False,
            headers={
                'X-Requested-With': 'XMLHTTPRequest', 
                'Cookie': self.get_login_cookie()
            }
        )
        self.assertEqual(response.code, 404)

    def tearDown(self):
        """
        Drop the database after every test
        """
        from mongoengine.connection import get_connection
        get_connection().drop_database('test_titan')


if __name__ == '__main__':
    unittest.main()
