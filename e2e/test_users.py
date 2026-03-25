# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.api.main import Database
from pisense.backend.classes import USER_ROLES

def test_create_delete_user():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        db.create_user("test_user_1", USER_ROLES.admin)

        users = db._get_rows("users")
        print(users)

        assert False
