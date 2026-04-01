# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import USER_ROLES, Project, Database
import pytest

@pytest.mark.order(1) # global scope
def test_create_get_projects():
    with TestClient(app): # Will run with lifecycle function
        db = Database()

        # Assume these work as intended, create_user() is tested elsewhere
        user1 = db.create_user("user_1_project", role=USER_ROLES.admin, email="user1@email.com")
        user2 = db.create_user("user_2_project", role=USER_ROLES.admin, email="user2@email.com")
        user3 = db.create_user("user_3_project", role=USER_ROLES.admin, email="user3@email.com")

        project_name = "test_project_base"
        description = ""
        public = False
        archived = False
        owner_id = user1.id

        project = db.create_project( name = project_name, owner_id = owner_id )
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
