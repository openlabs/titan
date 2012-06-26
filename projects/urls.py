# -*- coding: utf-8 -*-
"""
    urls


    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import tornado.web

from .views import(OrganisationHandler, OrganisationsHandler, HomePageHandler,
    SlugVerificationHandler, ProjectsHandler, ProjectHandler,
    ProjectSlugVerificationHandler)

U = tornado.web.URLSpec

HANDLERS = [
    U(r'/', HomePageHandler, name="home"),
    U(r'/my-organisations/', OrganisationsHandler,
        name="projects.organisations"),
    U(r'/([a-zA-Z0-9_-]+)', OrganisationHandler,
        name="projects.organisation"),
    U(r'/\+slug-check', SlugVerificationHandler,
        name="projects.organisations.slug-check"),
    U(r'/([a-zA-Z0-9_-]+)/projects/', ProjectsHandler,
        name="projects.projects"),
    U(r'/([a-zA-Z0-9-_]+)/([a-zA-Z0-9-_]+)', ProjectHandler,
        name="projects.project"),
    U(r'/([a-zA-Z0-9-_]+)/\+slug-check',
        ProjectSlugVerificationHandler,
        name="projects.project.slug-check")
]
