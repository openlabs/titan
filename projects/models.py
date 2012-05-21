# -*- coding: utf-8 -*-
"""
    models


    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) LTD
    :license: BSD, see LICENSE for more details.
"""
from mongoengine import Document, EmbeddedDocument
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
    name = StringField(required=True, verbose_name=_("Name"))


class User(MonstorUser):
    """
    Extend users to make it a part of Organisation
    """
    #: The organisations this user is a part of. The user can create new 
    #: projects in the organisation that the user is a member of
    organisations = ListField(
        ReferenceField(Organisation), verbose_name=_("Organisations")
    )


class ProjectMember(EmbeddedDocument):
    """
    Model for a member in a project
    """
    user = ReferenceField(User, required=True, verbose_name=_("User"))
    #: If the user is a project admin, the user can invite more users to the
    #: project.
    role = StringField(
        verbose_name=_("Project Admin"), choices=[
            ('admin', 'Admin. Invite users to project and delete comments'),
            ('participant', 'Participants can do everything except invite'),
            ('observer', 'Read only access to the project'),
        ],
        required=True
    )


class Project(Document):
    """
    Model for project
    """
    name = StringField(required=True, verbose_name=_("Name"))
    members = ListField(
        EmbeddedDocumentField(ProjectMember), verbose_name=_("Members")
    )


class FollowUp(EmbeddedDocument):
    """
    A follow up to a specific task
    """
    #: The follow up comment/message
    message = StringField(verbose_name=_("Message"))

    #: The status from which the change happened
    from_status = StringField(
        verbose_name=_("From Status"), choices=STATUS_CHOICES
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


class Task(Document):
    """
    A model for Tasks
    """
    title = StringField(required=True, verbose_name=_("Title"))
    status = StringField(
        required=True, verbose_name=_("Status"), choices=STATUS_CHOICES
    )
    due_date = DateTimeField(verbose_name=_("Due Date"))

    assigned_to = ReferenceField(
        User, required=True, verbose_name=_("Assigned to")
    )
    #: The list of users who have access to this document. If left empty, all
    #: users in the current project will have access to the document.     
    permissions = ListField(ReferenceField(User))

    #: The list of users who will be sent an alert on being sent an email
    watchers = ListField(ReferenceField(User))

    follow_ups = ListField(EmbeddedDocumentField(FollowUp))

    @property
    def hours(self):
        """
        A property to sum up all the time from every followups and return a
        timedelta object.

        #: TODO
        """
        return 0
