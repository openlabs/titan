# -*- coding: utf-8 -*-
"""
    test_models

    Test by creating data in the models

    :copyright: (c) 2012 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest2 as unittest
from mongoengine import connect, ValidationError, OperationError
from mongoengine.connection import _get_connection

from titan.projects.models import(Team, Organisation, User, Project,
    AccessControlList, FollowUp, TaskList, Task)
from monstor.utils.web import slugify


def create_project(user, name, slug, organisation):
    """
    Create a new project and return the object.

    :param user: User collection object
    :param name: The name of the project
    :param slug: The slug used for the project.
    :param organisation: The organisation the project belongs to.
    :return: Created project as Document
    """
    acl_admin = AccessControlList(
        team=Team(
            name="Admin", organisation=organisation, members=[user]
        ).save(), role="admin"
    )
    acl_participant = AccessControlList(
        team=Team(
            name="Participant", organisation=organisation, members=[user]
        ).save(), role="participant"
    )
    project = Project(
        name=name, organisation=organisation, acl=[acl_admin, acl_participant],
        slug=slugify(slug)
    )
    return project


class TestModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        connect("test_model")

    def setUp(self):
        new_user = User(
            name="Anoop sm",
            email="anoop.sm@openlabs.co.in",
        )
        new_user.set_password("openlabs")
        new_user.save()
        self.user = new_user

    def tearDown(self):
        """
        Drop each collection after each test.
        """
        User.drop_collection()
        Organisation.drop_collection()
        Team.drop_collection()
        Project.drop_collection()
        Task.drop_collection()
        TaskList.drop_collection()

    def test_0010_create_organisation(self):
        """
        Create an Organisation
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        self.assertEqual(Organisation.objects().count(), 1)

    def test_0020_unique_slug(self):
        """
        'slug' must be a unique value in Organisation.
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        organisation = Organisation(name="open lab", slug=slugify("open labs"))
        self.assertRaises(OperationError, organisation.save)

    def test_0030_organisation_required_fields(self):
        """
        Test the required fields of Organisation collection.
        """
        # 'slug' is a required field
        organisation = Organisation(name="openlabs")
        self.assertRaises(ValidationError, organisation.save)

        # 'name' is a required field
        organisation = Organisation(slug=slugify("open labs"))
        self.assertRaises(ValidationError, organisation.save)

    def test_0040_create_team(self):
        """
        Create a Team
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team = Team(
            name="Developers", organisation=organisation, members=[self.user]
        )
        team.save()
        self.assertEqual(Team.objects().count(), 1)

    def test_0050_team_required_fields(self):
        """
        Test the required fields of Team collection
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()

        # "organisation" is a required field
        team = Team(name="Developers", members=[self.user])
        self.assertRaises(ValidationError, team.save)

        # "name" is a required field
        team = Team(organisation=organisation, members=[self.user])
        self.assertRaises(ValidationError, team.save)

    def test_0060_teams_under_organisation(self):
        """
        Testing the number of teams under the organisation
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        team_developers = Team(
            name="Developers", organisation=organisation, members=[self.user]
        )
        team_developers.save()
        self.assertEqual(organisation.teams.count(), 1)
        team_participants = Team(
            name="participants", organisation=organisation, members=[self.user]
        )
        team_participants.save()
        self.assertEqual(organisation.teams.count(), 2)

    def test_0070_create_project(self):
        """
        Create project under organisation
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        project = create_project(
            self.user, "Titan", "titan project", organisation
        )
        project.save()
        self.assertEqual(Project.objects().count(), 1)

    def test_0080_unique_slug(self):
        """
        project "slug" must be unique under the current organisation
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        project = create_project(
            self.user, "New Titan", "titan projects", organisation
        )
        project.save()
        project = create_project(
            self.user, "New Titan", "titan projects", organisation
        )
        self.assertRaises(ValidationError, project.save)

    def test_0090_same_slug(self):
        """
        We can use same project "slug" under different organisations
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        project = create_project(
            self.user, "New Titan", "titan projects", organisation
        )
        project.save()
        new_organisation = Organisation(name="Infy", slug=slugify("infy labs"))
        new_organisation.save()
        project = create_project(
            self.user, "New Titan", "titan projects", new_organisation
        )
        project.save()

    def test_0100_project_required_fields(self):
        """
        Test the fields required for the Project collection.
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        # Create AccessControlList instances
        acl_developers = AccessControlList(
            team=Team(
                name="Admins", organisation=organisation, members=[self.user]
            ).save(), role="admin"
        )
        acl_participants = AccessControlList(
            team=Team(
                name="Viewers", organisation=organisation, members=[self.user]
            ).save(), role="participant"
        )

        # 'organisation' is a required field
        project = Project(
            name="titan", slug=slugify("titan project"), acl=[acl_developers,
            acl_participants]
        )
        self.assertRaises(ValidationError, project.save)

        # 'acl' is a a required field
        project = Project(name="New Titan", slug=slugify( "titan projects"),
            organisation=organisation
        )
        self.assertRaises(ValidationError, project.save)

        # 'name' is a required field
        project = Project(slug=slugify("titan project"),
            organisation=organisation, acl=[acl_developers, acl_participants]
        )
        self.assertRaises(ValidationError, project.save)

        # 'slug' is a required field
        project = Project(
            name="titan", organisation=organisation,
            acl=[acl_developers, acl_participants]
        )
        self.assertRaises(ValidationError, project.save)

    def test_0110_create_tasklist(self):
        """
        Create task list under project
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        project = create_project(
            self.user, 'Titan', 'titan project', organisation
        )
        project.save()
        task_list = TaskList(name="Version 0.1", project=project)
        task_list.save()
        self.assertEqual(TaskList.objects().count(), 1)

    def test_0120_tasklist_required_fields(self):
        """
        Test the required fields of TaskList
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        project = create_project(
            self.user, 'Titan', 'titan project', organisation
        )
        project.save()

        # 'project' is a required field
        task_list = TaskList(name="Version 0.1")
        self.assertRaises(ValidationError, task_list.save)

        # 'name' is a required field
        task_list = TaskList(project=project)
        self.assertRaises(ValidationError, task_list.save)

    def test_0130_create_task(self):
        """
        Create Task under Task List
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        project = create_project(
            self.user, 'Titan', 'titan project', organisation
        )
        project.save()
        task_list = TaskList(name="Version 0.1", project=project)
        task_list.save()
        follow_up = FollowUp(message="Any message", from_status="resolved")

        # Create Task
        task = Task(
            title="Create model design", status ="resolved",
            assigned_to=self.user, watchers=[self.user], task_list=task_list,
            follow_ups=[follow_up]
        )
        task.save()
        self.assertEqual(Task.objects().count(), 1)

    def test_0140_task_required_fields(self):
        """
        Test the fields required for the Task collection.
        """
        organisation = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation.save()
        project = create_project(
            self.user, 'Titan', 'titan project', organisation
        )
        project.save()
        task_list = TaskList(name="Version 0.1", project=project)
        task_list.save()
        follow_up = FollowUp(message="Any message", from_status="resolved")

        #"title"  is a required field        
        task = Task(
            status ="resolved", assigned_to=self.user, watchers=[self.user],
            task_list=task_list, follow_ups=[follow_up]
        )
        self.assertRaises(ValidationError, task.save)

        # "Status" is a required Field
        task = Task(
            title="Create model design", assigned_to=self.user,
            watchers=[self.user], task_list=task_list, follow_ups=[follow_up]
        )
        self.assertRaises(ValidationError, task.save)

        # "assigned_to" is a required field
        task = Task(
            title="Create model desi", status ="resolved",
            watchers=[self.user], task_list=task_list, follow_ups=[follow_up]
        )
        self.assertRaises(ValidationError, task.save)

        # "task_list" is a required field
        task = Task(
            title="Create model design", status ="resolved",
            assigned_to=self.user,
        )
        self.assertRaises(ValidationError, task.save)

    def test_0150_user_organisation(self):
        """
        Test the organisation property of user
        """
        user_2 = User(
            name="test-user",
            email="test@sample.com",
        )
        user_2.set_password("openlabs")
        user_2.save()

        # Create organisations
        organisation_1 = Organisation(
            name="open labs", slug=slugify("open labs")
        )
        organisation_1.save()
        organisation_2 = Organisation(
            name="new organisation", slug=slugify("new organisation")
        )
        organisation_2.save()

        # Create teams
        team_developers = Team(
            name="Developers", organisation=organisation_1,
            members=[self.user, user_2]
        )
        team_developers.save()
        team_participants = Team(
            name="Paricipants", organisation=organisation_2,
            members=[self.user]
        )
        team_participants.save()
        self.assertEqual(len(self.user.organisations), 2)
        self.assertEqual(len(user_2.organisations), 1)


    @classmethod
    def tearDownClass(cls):
        c = _get_connection()
        c.drop_database('test_model')


if __name__ == '__main__':
    unittest.main()

