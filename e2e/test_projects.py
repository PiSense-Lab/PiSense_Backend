# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import USER_ROLES, Project, Database, User
import pytest

@pytest.mark.order(1) # global scope
def test_create_get_projects():
    with TestClient(app): # Will run with lifecycle function
        db = Database()

        # Assume these work as intended, create_user() is tested elsewhere
        user1 = db.create_user("user_1_project", role=USER_ROLES.admin, email="user1@email.com", password="jkl")
        user2 = db.create_user("user_2_project", role=USER_ROLES.admin, email="user2@email.com", password="sds")
        user3 = db.create_user("user_3_project", role=USER_ROLES.admin, email="user3@email.com", password="wef")

        user1_2 = db.create_user("user_1_2_project", role=USER_ROLES.analyst, email="user1_2@email.com", password="jkl")
        user1_3 = db.create_user("user_1_3_project", role=USER_ROLES.viewer, email="user1_3@email.com", password="jkl")

        project_name = "test_project_base"
        description = ""
        public = False
        archived = False
        owner_id = user1.id

        project = db.create_project( name = project_name, owner_id = owner_id )
        project.add_user(user1_2.id, USER_ROLES.analyst)
        project.add_user(user1_3.id, USER_ROLES.viewer)
        print("User object from `create_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived
        assert project.owner_id == owner_id

        users = project.users
        possible_users = [ user1, user1_2, user1_3]

        print("- - - users - - -")
        print(users)
        assert len(users) == 3

        for up in users:
            user = up['user']
            role = up['role']
            assert isinstance(user, User)

            u: User | None = None
            for puser in possible_users:
                if user.id == puser.id:
                    u = puser
                    break

            assert not isinstance(u, type(None))

            assert u.id == user.id
            assert u.email == user.email
            assert u.role == u.role
            assert u.username == u.username
            assert u.role == role


        project = db.get_project( name = project_name)
        print("User object from `get_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived
        assert project.owner_id == owner_id

        for up in users:
            user = up['user']
            role = up['role']
            assert isinstance(user, User)

            u: User | None = None
            for puser in possible_users:
                if user.id == puser.id:
                    u = puser
                    break

            assert not isinstance(u, type(None))

            assert u.id == user.id
            assert u.email == user.email
            assert u.role == u.role
            assert u.username == u.username
            assert u.role == role


        project_name = "test_project_public"
        description = "some description"
        public = True
        archived = False
        owner_id = user2.id

        project = db.create_project( name = project_name, owner_id = owner_id, description=description, public=public)
        print("User object from `create_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived
        assert project.owner_id == owner_id

        project = db.get_project( name = project_name)
        print("User object from `get_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived
        assert project.owner_id == owner_id


        project_name = "test_project_public_archived"
        description = "some description 2"
        public = True
        archived = True
        owner_id = user3.id

        project = db.create_project( name = project_name, owner_id = owner_id, description=description, public=public, archived=archived)
        print("User object from `create_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived
        assert project.owner_id == owner_id

        project = db.get_project( name = project_name)
        print("User object from `get_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived
        assert project.owner_id == owner_id

        projects = db.get_projects()
        assert len(projects) == 3
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))
            assert not isinstance(project.owner_id, type(None))

        projects = db.get_projects("test_project")
        assert len(projects) == 3
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))
            assert not isinstance(project.owner_id, type(None))

        projects = db.get_projects("test_project_public")
        assert len(projects) == 2
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))
            assert not isinstance(project.owner_id, type(None))

        projects = db.get_projects("archived")
        assert len(projects) == 1
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))
            assert not isinstance(project.owner_id, type(None))

        projects = db.get_projects("somthing_random")
        assert len(projects) == 0
