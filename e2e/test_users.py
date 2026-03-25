# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import USER_ROLES, User, Database


def test_create_delete_user():
    with TestClient(app): # Will run with lifecycle function
        db = Database()

        username = "test_username_admin"
        role = USER_ROLES.admin
        db.create_user(username, role)
        user = db.get_user(username=username)
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role

        username = "test_username_analyst_goodemail@email.com"
        role = USER_ROLES.analyst
        email = 'goodemail@email.com'
        db.create_user(username=username, role=role, email=email)
        user = db.get_user(username=username)
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email

        username = "test_username_analyst_goodemail@email.com"
        role = USER_ROLES.viewer
        email = 'goodemail@email.com'
        firstname = 'bill'
        lastname = 'frank'
        password = 'definitely_hashed'
        db.create_user(username=username, role=role, email=email, firstname=firstname, lastname=lastname, password=password)
        user = db.get_user(username=username)
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email
        assert user.firstname == firstname
        assert user.lastname == lastname
