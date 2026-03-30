# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import Project, Database


def test_create_get_projects():
    with TestClient(app): # Will run with lifecycle function
        db = Database()

# CREATE TABLE projects (
#     project_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
#     project_name VARCHAR(100) NOT NULL,
#     description TEXT DEFAULT NULL,
#     public TINYINT(1) DEFAULT NULL,
#     archived TINYINT(1) DEFAULT NULL
# );

        project_name = "test_project_base"
        description = ""
        public = False
        archived = False

        db.create_project( name = project_name, description=description, public=public, archived=archived)
        db.create_project( name = project_name )
        project = db.get_project( name = project_name)
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived


        project_name = "test_project_public"
        description = "some description"
        public = True
        archived = False

        db.create_project( name = project_name, description=description, public=public)
        db.create_project( name = project_name )
        project = db.get_project( name = project_name)
        print(project)
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.name == project_name
        assert project.description == description
        assert project.public == public
        assert project.archived == archived

        project_name = "test_project_public_archived"
        description = "some description"
        public = True
        archived = True

        db.create_project( name = project_name, description=description, public=public, archived=archived)
        db.create_project( name = project_name )
        project = db.get_project( name = project_name)
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
