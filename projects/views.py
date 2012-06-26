# -*- coding: utf-8 -*-
"""
    views

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import tornado
from wtforms import Form, TextField, StringField, SelectField
from monstor.utils.wtforms import REQUIRED_VALIDATOR, TornadoMultiDict
from monstor.utils.web import BaseHandler
from monstor.utils.i18n import _

from .models import User, Organisation, Team, Project, AccessControlList


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
            team = Team(
                name="Administrators", organisation=organisation,
                memebers=[self.current_user]
            )
            team.save()
            self.flash(
                _("Created a new organisation %(name)s",
                    name=organisation.name
                ), "info"
            )
            self.redirect(
                self.reverse_url('projects.organisation', organisation.slug)
            )
            return
        self.render("projects/organisations.html", organisation_form=form)


class OrganisationHandler(BaseHandler):
    """
    An Element URI
    """

    @tornado.web.authenticated
    @tornado.web.removeslash
    def get(self, slug):
        """
        Render organisation page
        """
        current_user = User.objects.with_id(self.current_user.id)
        for organisation in current_user.organisations:
            if organisation.slug == slug:
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


class ProjectForm(Form):
    """
    Generate form for creating a project
    """
    name = TextField("name", [REQUIRED_VALIDATOR])
    slug = StringField("slug", [REQUIRED_VALIDATOR])
    team = SelectField("team", [REQUIRED_VALIDATOR], choices=[])


class ProjectsHandler(BaseHandler):
    """
    Handles projects
    """
    @tornado.web.authenticated
    @tornado.web.addslash
    def get(self, organisation_slug):
        """
        Projects under the current organisations
        """
        for organisation in self.current_user.organisations:
            if organisation.slug == organisation_slug:
                break
        else:
            raise tornado.web.HTTPError(404)

        projects = Project.objects(organisation=organisation).all()
        if self.is_xhr:
            self.write({
                'result': [
                    {
                        'id': project.id,
                        'name': project.name,
                    } for project in projects
                ]
            })
        else:
            form=ProjectForm()
            form.team.choices = [
                (unicode(team.id), team.name) for team in organisation.teams
            ]
            self.render(
                'projects/projects.html', projects=projects, form=form
            )
        return

    @tornado.web.authenticated
    def post(self, organisation_slug):
        """
        Accept the form fields and create a new project under the
        current Organisation
        """
        form = ProjectForm(TornadoMultiDict(self))
        for organisation in self.current_user.organisations:
            if organisation.slug == organisation_slug:
                break
        else:
            raise tornado.web.HTTPError(404)

        form.team.choices = [
            (unicode(team.id), team.name) for team in organisation.teams
        ]

        existing = Project.objects(
            slug=form.slug.data, organisation=organisation
        ).first()
        if existing:
            self.flash(
                _(
                    "A project with the same short code already exists with\
                    in current organisation."
                ), 'Warning'
            )
        elif form.validate():
            admin_team = Team.objects().with_id(form.team.data)
            if self.current_user not in admin_team.members:
                self.flash(
                    _(
                        "You are not an administrator. Only administrators can\
                         create projects"
                    )
                )
                self.send_error(403)
                return
            acl_admin = AccessControlList(team=admin_team, role="admin")
            project = Organisation(
                name = form.name.data,
                acl = [acl_admin],
                slug = form.slug.data,
                organisation = organisation
            )
            project.save()
            self.flash(
                _("Created a new project %(name)s",
                    name=project.name
                ), "info"
            )
            self.redirect(
                self.reverse_url(
                    'projects.project', organisation.slug,
                    project.slug
                )
            )
            return
        self.render("projects/projects.html", form=form)


class ProjectSlugVerificationHandler(BaseHandler):
    """
    A handler that should help AJAX implementation of checking if a slug can
    be used for the project under current organisation.
    """
    @tornado.web.authenticated
    def post(self, organisation_slug):
        """
        Accept a string and check if any existing project under current
        organisation uses that string as a slug.

        The return value is a 'true' or 'false' which are valid javascript
        literals which can be safely `eval`ed
        """
        project_slug = self.get_argument("project_slug")
        for organisation in self.current_user.organisations:
            if organisation.slug == organisation_slug:
                break
        else:
            raise tornado.web.HTTPError(404)
        project = Project.objects(
            slug=project_slug,
            organisation=organisation
        ).first()
        if not project:
            self.write('true')
        else:
            self.write('false')


class ProjectHandler(BaseHandler):
    """
    Handle a particular project
    """
    @tornado.web.authenticated
    def get(self, organisation_slug, project_slug):
        """
        Render project page
        """
        for organisation in self.current_user.organisations:
            if organisation.slug == organisation_slug:
                break
        else:
            raise tornado.web.HTTPError(404)
        project = Project.objects(
            slug=project_slug, organisation=organisation
        ).first()
        if not project:
            raise tornado.web.HTTPError(404)

        # Response
        if self.is_xhr:
            self.write({
                'id': project.id,
                'name': project.name,
            })
        else:
            self.render(
                'projects/project.html', project=project
            )
        return
