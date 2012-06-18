# -*- coding: utf-8 -*-
"""
    urls


    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import tornado.web

from .views import(OrganisationHandler, OrganisationsHandler, HomePageHandler,
    SlugVerificationHandler)

U = tornado.web.URLSpec

HANDLERS = [
    U(r'/', HomePageHandler, name="home"),
    U(r'/organisations/', OrganisationsHandler, name="projects.organisations"),
    U(r'/organisations/([a-zA-Z0-9_-]+)', OrganisationHandler,
        name="projects.organisation"),
    U(r'/organisations/\+slug-check', SlugVerificationHandler,
        name="projects.organisations.slug-check"),
]
