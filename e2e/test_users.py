# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import USER_ROLES, User, Database


def test_create_get_users():
    with TestClient(app): # Will run with lifecycle function
        db = Database()


        username = "test_username_admin"
        email = "blank@email.com"
        password = "defnitly_hashed"
        role = USER_ROLES.admin

        user = db.create_user(username=username, role=role, email=email, password=password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email
        assert user.password == password

        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email
        assert user.password == password


        username = "test_username_analyst_email"
        role = USER_ROLES.analyst
        email = 'goodemail@email.com'
        password = "defnitly_hashed"

        user = db.create_user(username=username, role=role, email=email, password=password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email
        assert user.password == password

        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email
        assert user.password == password


        username = "test_username_viewer_email_firstname"
        role = USER_ROLES.viewer
        email = 'goodemail2@email.com'
        firstname = 'bill'
        lastname = 'frank'
        password = 'definitely_hashed'

        user = db.create_user(username=username, role=role, email=email, firstname=firstname, lastname=lastname, password=password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email
        assert user.password == password
        assert user.firstname == firstname
        assert user.lastname == lastname

        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.role == role
        assert user.email == email
        assert user.password == password
        assert user.firstname == firstname
        assert user.lastname == lastname


        users = db.get_users()
        assert len(users) == 3
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.password, type(None))

        users = db.get_users("test_username")
        assert len(users) == 3
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.password, type(None))

        users = db.get_users("email")
        assert len(users) == 2
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.password, type(None))

        users = db.get_users("firstname")
        assert len(users) == 1
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.role, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.password, type(None))

        users = db.get_users("somthing_random")
        assert len(users) == 0
