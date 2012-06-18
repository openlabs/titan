# -*- coding: utf-8 -*-
"""
    views

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import tornado
from wtforms import Form, TextField, StringField
from monstor.utils.wtforms import REQUIRED_VALIDATOR, TornadoMultiDict
from monstor.utils.web import BaseHandler
from monstor.utils.i18n import _

from .models import User, Organisation


class HomePageHandler(BaseHandler):
    """
    A home page handler
    """
    def get(self):
        self.write("Welcome home")


class OrganisationForm(Form):
    """
    Generate Form for creating an organisation
    """
    name = TextField("name", [REQUIRED_VALIDATOR])
    slug = StringField("slug", [REQUIRED_VALIDATOR])


class SlugVerificationHandler(BaseHandler):
    """
    A handler that should help AJAX implementation of checking if a slug can
    be used for the organisation.
    """
    @tornado.web.authenticated
    def post(self):
        """
        Accept a string and check if any existing organisation uses that
        string as a slug.
        
        The return value is a 'true' or 'false' which are valid javascript
        literals which can be safely `eval`ed
        """
        slug = self.get_argument("slug")
        organisation = Organisation.objects(slug=slug).first()
        if not organisation:
            self.write('true')
        else:
            self.write('false')


class OrganisationsHandler(BaseHandler):
    """
    A Collections Handler
    """

    @tornado.web.authenticated
    @tornado.web.addslash
    def get(self):
        """
        The organisations of the current user
        """
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
                'projects/organisations.html', organisations=user_orgs,
                form=OrganisationForm()
            )
        return

    @tornado.web.authenticated
    @tornado.web.addslash
    def post(self):
        """
        Accept the form fields and create new organisation under current user.
        """
        form = OrganisationForm(TornadoMultiDict(self))
        organisation = Organisation.objects(slug=form.slug.data).first()
        if organisation:
            self.flash(
                _(
                    "An organisation with the same short code already exists."
                ), 'Warning'
            )
        elif form.validate():
            organisation = Organisation(
                name = form.name.data,
                slug = form.slug.data
            )
            organisation.save()
            organisation_id = organisation.id
            self.flash(
                _("Created a new organisation %(name)s",
                    name=organisation.name
                ), "info"
            )
            self.redirect(
                self.reverse_url('projects.organisation', organisation_id)
            )
            return
        self.render("projects/organisations.html", organisation_form=form)


class OrganisationHandler(BaseHandler):
    """
    An Element URI
    """

    @tornado.web.authenticated
    @tornado.web.removeslash
    def get(self, organisation_id):
        """
        Render organisation page
        """
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
