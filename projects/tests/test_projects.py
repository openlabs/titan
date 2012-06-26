# -*- coding: utf-8 -*-
"""
    test_projects

    Test the projects API

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest
import json
from urllib import urlencode

from tornado import testing, options
from monstor.app import make_app
from titan.projects.models import (User, Project, Organisation, Team,
    AccessControlList)
from titan.settings import SETTINGS
from monstor.utils.web import slugify


class TestOrganisations(testing.AsyncHTTPTestCase):

    def get_app(self):
        options.options.database = 'test_project'
        SETTINGS['xsrf_cookies'] = False
        application = make_app(**SETTINGS)
        return application

    def setUp(self):
        super(TestOrganisations, self).setUp()
        user = User(name="Test User", email="test@example.com", active=True)
        user.set_password("password")
        user.save(safe=True)
        self.user = user

    def get_login_cookie(self):
        response = self.fetch(
            '/login', method="POST", follow_redirects=False,
            body=urlencode({
                'email': 'test@example.com', 'password': 'password'
            })
        )
        return response.headers.get('Set-Cookie')

    def test_0010_projectshandler_get(self):
        """
        Test ProjectsHandler 'get' method
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation,
            members=[self.user]
        )
        team.save()

        # User not logged in
        response = self.fetch(
            '/%s/projects/' % organisation.slug,
            method="GET",
            follow_redirects=False
        )
        self.assertEqual(response.code, 302)

        # User logged in and an existing organisation
        cookies = self.get_login_cookie()
        response = self.fetch(
            '/%s/projects/' % organisation.slug,
            method="GET",
            follow_redirects=False,
            headers ={'Cookie' : cookies}
        )
        self.assertEqual(response.code, 200)

        # User logged in and Organisation not existing
        cookies = self.get_login_cookie()
        response = self.fetch(
            '/an-invalid-url/projects/',
            method="GET",
            follow_redirects=False,
            headers ={'Cookie' : cookies}
        )
        self.assertEqual(response.code, 404)

    def test_0020_projectshandler_post_1(self):
        """
        Test post with logged in and project slug does not exists
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation,
            members=[self.user]
        )
        team.save()
        cookies = self.get_login_cookie()
        response = self.fetch(
            '/%s/projects/' % organisation.slug,
            method="POST",
            follow_redirects=False,
            headers ={'Cookie' : cookies},
            body=urlencode({'name':'Titan', 'slug':'titan', 'team': str(team.id)}),
        )
        self.assertEqual(response.code, 302)

    def test_0040_projectshandler_post_2(self):
        """
        post with logged in and Project slug already exist
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation,
            members=[self.user]
        )
        team.save()
        acl = AccessControlList(team=team, role="admin")
        project =Project(
            name="titan", organisation=organisation, acl=[acl],
            slug=slugify('titan project')
        )
        project.save()
        response = self.fetch(
            '/%s/projects/' % organisation.slug,
            method="POST",
            follow_redirects=False,
            body=urlencode({'name':'Titan', 'slug':slugify('titan project')}),
            headers= {'Cookie' : self.get_login_cookie()}
        )
        self.assertEqual(response.code, 200)
        self.assertEqual(
            response.body.count(
                u'A project with the same short code already exists'
            ), 1
        )


    def test_0050_slugverificationhandler_1(self):
        """
        Verify project slug which does not exists under current organisations
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation,
            members=[self.user]
        )
        team.save()
        response = self.fetch(
            '/%s/+slug-check' % organisation.slug,
            method="POST",
            follow_redirects=False,
            body=urlencode({
                'project_slug':slugify('titan project')
            }),
            headers= {'Cookie' : self.get_login_cookie()}
        )
        response = json.loads(response.body)
        self.assertEqual(response, True)

    def test_0060_slugverificationhandler_2(self):
        """
        Verify project slug which already exists under current organisations
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation,
            members=[self.user]
        )
        team.save()
        acl = AccessControlList(team=team, role="admin")
        project =Project(
            name="titan", organisation=organisation, acl=[acl],
            slug=slugify('titan project')
        )
        project.save()
        response = self.fetch(
            '/%s/+slug-check' % organisation.slug,
            method="POST",
            follow_redirects=False,
            body=urlencode({
                'project_slug':slugify('titan project')
            }),
            headers= {'Cookie' : self.get_login_cookie()}
        )
        response = json.loads(response.body)
        self.assertEqual(response, False)

    def test_0070_projecthandler_1(self):
        """
        Test project page which already exist
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation,
            members=[self.user]
        )
        team.save()
        acl = AccessControlList(team=team, role="admin")
        project =Project(
            name="titan", organisation=organisation, acl=[acl],
            slug=slugify('titan project')
        )
        project.save()
        response = self.fetch(
            '/%s/%s' % (organisation.slug, project.slug),
            method="GET",
            follow_redirects=False,
            headers= {'Cookie' : self.get_login_cookie()}
        )
        self.assertEqual(response.code, 200)

    def test_0080_projecthandler_2(self):
        """
        Test project page which does not exist
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation,
            members=[self.user]
        )
        team.save()
        response = self.fetch(
            '/%s/an-invalid-slug' % organisation.slug,
            method="GET",
            follow_redirects=False,
            headers= {'Cookie' : self.get_login_cookie()}
        )
        self.assertEqual(response.code, 404)

    def tearDown(self):
        """
        Drop the database after every test
        """
        from mongoengine.connection import get_connection
        get_connection().drop_database('test_project')


if __name__ == '__main__':
    unittest.main()
