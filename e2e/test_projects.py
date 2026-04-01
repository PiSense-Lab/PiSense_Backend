# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import Project, Database


def test_create_get_projects():
    with TestClient(app): # Will run with lifecycle function
        db = Database()


        project_name = "test_project_base"
        description = ""
        public = False
        archived = False

        project = db.create_project( name = project_name )
        print("User object from `create_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived

        project = db.get_project( name = project_name)
        print("User object from `get_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived
        assert project.archived == archived


        project_name = "test_project_public"
        description = "some description"
        public = True
        archived = False

        project = db.create_project( name = project_name, description=description, public=public)
        print("User object from `create_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived

        project = db.get_project( name = project_name)
        print("User object from `get_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived


        project_name = "test_project_public_archived"
        description = "some description 2"
        public = True
        archived = True

        project = db.create_project( name = project_name, description=description, public=public, archived=archived)
        print("User object from `create_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived

        project = db.get_project( name = project_name)
        print("User object from `get_project`")
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived

        projects = db.get_projects()
        assert len(projects) == 3
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))

        projects = db.get_projects("test_project")
        assert len(projects) == 3
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))

        projects = db.get_projects("test_project_public")
        assert len(projects) == 2
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))

        projects = db.get_projects("archived")
        assert len(projects) == 1
        for project in projects:
            assert isinstance(project, Project)
            assert not isinstance(project.name, type(None))
            assert not isinstance(project.id, type(None))

        projects = db.get_projects("somthing_random")
        assert len(projects) == 0
