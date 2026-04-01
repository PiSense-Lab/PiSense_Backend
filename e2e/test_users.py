# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import USER_ROLES, User, Database


def test_create_get_users():
    with TestClient(app): # Will run with lifecycle function
        db = Database()

        username = "test_username_admin"
        role = USER_ROLES.admin
        user = db.create_user(username, role)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role

        username = "test_username_analyst_email"
        role = USER_ROLES.analyst
        email = 'goodemail@email.com'
        user = db.create_user(username=username, role=role, email=email)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role

        username = "test_username_viewer_email_firstname"
        role = USER_ROLES.viewer
        email = 'goodemail@email.com'
        firstname = 'bill'
        lastname = 'frank'
        password = 'definitely_hashed'
        user = db.create_user(username=username, role=role, email=email, firstname=firstname, lastname=lastname, password=password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role

        users = db.get_users()
        assert len(users) == 3
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))

        users = db.get_users("test_username")
        assert len(users) == 3
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))

        users = db.get_users("email")
        assert len(users) == 2
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))

        users = db.get_users("firstname")
        assert len(users) == 1
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))

        users = db.get_users("somthing_random")
        assert len(users) == 0
