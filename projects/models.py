# -*- coding: utf-8 -*-
"""
    models


    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) LTD
    :license: BSD, see LICENSE for more details.
"""
from mongoengine import Document, EmbeddedDocument, ValidationError
from mongoengine import (StringField, ReferenceField, ListField, FileField,
    DateTimeField, EmbeddedDocumentField)
from monstor.utils.i18n import _
from monstor.contrib.auth.models import User as MonstorUser


STATUS_CHOICES = [
    ('new', 'New'),
    ('in-progress', 'In Progress'),
    ('hold', 'Hold'),
    ('resolved', 'Resolved'),
]


class Organisation(Document):
    """
    Model for Organisation
    """

    #: The Organisation name
    name = StringField(
        required=True, verbose_name=_("Name")
    )

    #: Upload the image for the organisation
    image = FileField(verbose_name=_("Image"))

    #: Short identifier for the organisation, used in url
    slug = StringField(verbose_name=_("Slug"), required=True, unique=True)

    @property
    def teams(self):
        return Team.objects(organisation=self).all()


class User(MonstorUser):
    """
    Extend users to make it a part of Organisation
    """

    @property
    def organisations(self):
        # Find list of teams the user is a part of
        # Find the set of organisations the lists belong to
        # That is the the list of organisations the user belongs to
        raise Exception("Not implemented yet")


class Team(Document):
    """
    Teams are collection of Users under an Organisation
    This logical separation allows ACL on Projects
    """

    #: Provide the name for the team
    name = StringField(required=True, verbose_name=_("Name"))

    #: The organisation the Team belongs to
    organisation = ReferenceField(
        Organisation, required=True, verbose_name=_("Organisation")
    )

    #: The list of members in the team
    members = ListField(
        ReferenceField(User), verbose_name=_("Members")
    )


class AccessControlList(EmbeddedDocument):
    """
    Model for a member in a project
    """
    team = ReferenceField(Team, required=True, verbose_name=_("Team"))

    #: If the user is a project admin, the user can invite more users to the
    #: project.
    role = StringField(
        verbose_name=_("Role"), choices=[
            ('admin', _('Admin.Invite users to project and delete comments')),
            ('participant', _('Participants can do everything except invite')),
            ('observer', _('Read only access to the project')),
        ],
        required=True
    )


class Project(Document):
    """
    Model for project
    """

    #: The name of the project
    name = StringField(required=True, verbose_name=_("Name"))

    #: The list of tems in the project
    acl = ListField(
        EmbeddedDocumentField(AccessControlList), verbose_name=_("ACL"),
        required=True
    )

    #: Short identifier for the project, used in url
    slug = StringField(verbose_name=_("Slug"), required=True)

    #: The name of the organisation, under which this project exist
    organisation = ReferenceField(
        Organisation, verbose_name=_("Organisation"), required=True
    )

    def validate(self):
        """
        Whenever we create a new project or update an existing project object,
        validates the slug field to ensure that the slug is unique under the
        current organisation. If the slug is already existing raise a
        validation error.
        """
        super(Project, self).validate()
        duplicate = Project.objects(
            organisation=self.organisation,
            slug=self.slug,
        )
        if (len(duplicate) > 1) or (duplicate and duplicate[0].id != self.id):
            raise ValidationError(
                "Duplicate %s: %s" % ("slug", self.slug)
            )


class FollowUp(EmbeddedDocument):
    """
    A follow up to a specific task
    """

    #: The follow up comment/message
    message = StringField(verbose_name=_("Message"))

    #: The status from which the change happened
    from_status = StringField(
        verbose_name=_("From Status"), default="new",
        choices=STATUS_CHOICES
    )

    #: The end state
    to_status = StringField(
        verbose_name=_("To Status"), choices=STATUS_CHOICES
    )

    #: The due date prior to this update
    from_due_date = DateTimeField(verbose_name=_("From Due Date"))

    #: The new due date
    to_due_date = DateTimeField(verbose_name=_("To Due Date"))

    #: File fields are stored in GridFS and only a reference to them is 
    #: held here. See 
    #: http://mongoengine-odm.readthedocs.org/en/latest/guide/gridfs.html
    attachments = ListField(FileField(), verbose_name=_("Attachments"))


class TaskList(Document):
    """
    A model for Task list
    """

    #: The name of the task list
    name = StringField(required=True, verbose_name=_("Name"))

    #: The name of the project, under which this task list exist
    project = ReferenceField(Project, required=True, verbose_name=_("Project"))


class Task(Document):
    """
    A model for Tasks
    """

    #: The title of the task
    title = StringField(required=True, verbose_name=_("Title"))

    #: The status of the current task
    status = StringField(
        required=True, verbose_name=_("Status"), choices=STATUS_CHOICES
    )
    due_date = DateTimeField(verbose_name=_("Due Date"))

    #: The name of the user, who has assigned this task
    assigned_to = ReferenceField(
        User, required=True, verbose_name=_("Assigned to")
    )
    
    #: The list of users who will be sent an alert on being sent an email
    watchers = ListField(ReferenceField(User))

    #: The reference to the task list
    task_list = ReferenceField(TaskList, required=True)
    follow_ups = ListField(EmbeddedDocumentField(FollowUp))

    @property
    def hours(self):
        """
        A property to sum up all the time from every followups and return a
        timedelta object.

        #: TODO
        """
        return 0
