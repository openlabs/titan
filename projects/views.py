# -*- coding: utf-8 -*-
"""
    views

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import tornado
from wtforms import Form, TextField, validators
from monstor.utils.wtforms import REQUIRED_VALIDATOR, EMAIL_VALIDATOR, \
    TornadoMultiDict
from monstor.utils.web import BaseHandler
from monstor.utils.i18n import _

from .models import User 


class HomePageHandler(BaseHandler):
    """
    A home page handler
    """
    def get(self):
        self.write("Welcome home")


class OrganisationForm(Form):
    name = TextField("Name", [REQUIRED_VALIDATOR])


class OrganisationsHandler(BaseHandler):
    """
    A Collections Handler
    """
    @tornado.web.authenticated
    @tornado.web.addslash
    def get(self):
        # The organisations of the current user
        current_user = User.objects.with_id(self.current_user.id)
        user_orgs = current_user.organisations

        if self.is_xhr:
            self.write({
                'result': [
                    {
                        'id': o.id,
                        'name': o.name,
                    } for o in user_orgs
                ]
            })
        else:
            self.render(
                'projects/organisations.html', organisations=user_orgs
            )
        return


class OrganisationHandler(BaseHandler):
    """
    An Element URI
    """

    @tornado.web.authenticated
    @tornado.web.removeslash
    def get(self, organisation_id):
        current_user = User.objects.with_id(self.current_user.id)
        user_orgs = current_user.organisations

        for organisation in user_orgs:
            if organisation.id == organisation_id:
                break
        else:
            raise tornado.web.HTTPError(404)

        # Response
        if self.is_xhr:
            self.write({
                'id': organisation.id,
                'name': organisation.name,
            })
        else:
            self.render(
                'projects/organisation.html', organisation=organisation
            )
        return
