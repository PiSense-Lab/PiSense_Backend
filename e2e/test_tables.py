# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.api.main import Database
import pytest

@pytest.mark.order(0) # global scope
def test_get_datasets():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        datasets = db._get_rows("dataset") # noqa: F841

@pytest.mark.order(0) # global scope
def test_get_projects_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        projects = db._get_rows("projects") # noqa: F841

@pytest.mark.order(0) # global scope
def test_get_roles_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        roles = db._get_rows("roles") # noqa: F841

@pytest.mark.order(0) # global scope
def test_get_user_projects_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        user_projects = db._get_rows("user_projects") # noqa: F841

@pytest.mark.order(0) # global scope
def test_get_users_table():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        users = db._get_rows("users") # noqa: F841
