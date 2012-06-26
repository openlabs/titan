# -*- coding: utf-8 -*-
"""
    test_organisations

    Test the organisations API

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import json
from urllib import urlencode

from tornado import testing, options
from monstor.app import make_app
from titan.projects.models import User, Organisation
from titan.settings import SETTINGS
from monstor.utils.web import slugify


class TestOrganisations(testing.AsyncHTTPTestCase):

    def get_app(self):
        options.options.database = 'test_titan'
        SETTINGS['xsrf_cookies'] = False
        application = make_app(**SETTINGS)
        return application

    def setUp(self):
        super(TestOrganisations, self).setUp()
        user = User(name="Test User", email="test@example.com", active=True)
        user.set_password("password")
        user.save(safe=True)

    def get_login_cookie(self):
        response = self.fetch(
            '/login', method="POST", follow_redirects=False,
            body=urlencode({
                'email': 'test@example.com', 'password': 'password'
            })
        )
        return response.headers.get('Set-Cookie')

    def test_0020_get_applications(self):
        """
        Test the HTML response
        """
        response = self.fetch(
            '/my-organisations/', method="GET", follow_redirects=False
        )
        self.assertEqual(response.code, 302)

        cookies = self.get_login_cookie()
        response = self.fetch(
            '/my-organisations/', method="GET", follow_redirects=False,
            headers ={'Cookie' : cookies}
        )
        self.assertEqual(response.code, 200)

    def test_0030_get_applications(self):
        """
        Test the JSON response
        """
        response = self.fetch(
            '/my-organisations/', method="GET", follow_redirects=False,
            headers={'X-Requested-With': 'XMLHTTPRequest'}
        )
        self.assertEqual(response.code, 302)

    def test_0040_get_invalid_organisation(self):
        """
        Try to GET and org which doesnt exist and look for 302 when not logged
        in and a 404 when logged in
        """
        response = self.fetch(
            '/an-invalid-org', method="GET",
            follow_redirects=False,
        )
        self.assertEqual(response.code, 302)

        response = self.fetch(
            '/an-invalid-org', method="GET",
            follow_redirects=False,
            headers={
                'X-Requested-With': 'XMLHTTPRequest',
                'Cookie': self.get_login_cookie()
            }
        )
        self.assertEqual(response.code, 404)

    def test_0050_slug_verification_1(self):
        """
        Verify slug which does not exists
        """
        slug = slugify("a new organisation")
        response = self.fetch(
            '/+slug-check', method="POST",
            follow_redirects=False,
            headers={
                'Cookie': self.get_login_cookie()
            },
            body=urlencode({
                "slug": slug
            })
        )
        response = json.loads(response.body)
        self.assertEqual(response, True)

    def test_0060_slug_verification_2(self):
        """
        verify slug which already exists
        """
        organisation = Organisation(
            name="openlabs", slug=slugify("new organisation")
        )
        organisation.save()
        slug = slugify("new organisation")
        response = self.fetch(
            '/+slug-check', method="POST",
            follow_redirects=False,
            headers={
                'Cookie': self.get_login_cookie()
            },
            body=urlencode({
                "slug": slug
            })
        )
        response = json.loads(response.body)
        self.assertEqual(response, False)

    def test_0070_create_organisation_1(self):
        """
        Test for creating an organisation which is does not exists
        """
        slug = slugify('new organisation')
        cookies = self.get_login_cookie()
        response = self.fetch(
            '/my-organisations/', method="POST", follow_redirects=False,
            headers={
                'Cookie': cookies
            },
            body=urlencode({
                'name': 'organisation', 'slug': slug
            })
        )
        self.assertEqual(response.code, 302)

    def test_0080_create_organisation_2(self):
        """
        Test for creating an organisation which already existing
        """
        organisation = Organisation(
            name="openlabs", slug=slugify("new organisation")
        )
        organisation.save()
        cookies = self.get_login_cookie()
        slug = slugify('new organisation')
        response = self.fetch(
            '/my-organisations/', method="POST", follow_redirects=False,
            headers={
                'Cookie': cookies
            },
            body=urlencode({
                'name': 'organisation', 'slug': slug
            })
        )
        self.assertEqual(response.code, 200)

    def test_0090_create_organisation_3(self):
        """
        Test for creating an organisation with empty form fields
        """
        slug = slugify('new organisation')
        cookies = self.get_login_cookie()
        response = self.fetch(
            '/my-organisations/', method="POST", follow_redirects=False,
            headers={
                'Cookie': cookies
            },
            body=urlencode({
                'name': 'organisation',
            })
        )
        self.assertEqual(response.code, 200)

    def tearDown(self):
        """
        Drop the database after every test
        """
        from mongoengine.connection import get_connection
        get_connection().drop_database('test_titan')


if __name__ == '__main__':
    unittest.main()
