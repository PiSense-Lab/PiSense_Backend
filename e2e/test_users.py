# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import User, Database
import pytest

@pytest.mark.order(0) # global scope
def test_create_get_users():
    with TestClient(app): # Will run with lifecycle function
        db = Database()

        username = "test_username_admin"
        email = "blank@email.com"
        hashed_password = "defnitly_hashed"

        user = db.create_user(username=username, email=email, password=hashed_password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.email == email


        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.email == email


        username = "test_username_analyst_email"
        email = 'goodemail@email.com'
        hashed_password = "defnitly_hashed"

        user = db.create_user(username=username, email=email, password=hashed_password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.email == email


        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.email == email


        username = "test_username_viewer_email_firstname"
        email = 'goodemail2@email.com'
        firstname = 'bill'
        lastname = 'frank'
        hashed_password = 'definitely_hashed'

        user = db.create_user(username=username, email=email, firstname=firstname, lastname=lastname, password=hashed_password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.email == email
        assert user.firstname == firstname
        assert user.lastname == lastname

        user = db.get_user(username=username)
        print("User from get_user")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.email == email
        assert user.firstname == firstname
        assert user.lastname == lastname


        users = db.get_users()
        assert len(users) == 3
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.hashed_password, type(None))

        users = db.get_users("test_username")
        assert len(users) == 3
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.hashed_password, type(None))

        users = db.get_users("email")
        assert len(users) == 2
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.hashed_password, type(None))

        users = db.get_users("firstname")
        assert len(users) == 1
        for user in users:
            assert isinstance(user, User)
            assert not isinstance(user.username, type(None))
            assert not isinstance(user.id, type(None))
            assert not isinstance(user.email, type(None))
            assert not isinstance(user.hashed_password, type(None))

        users = db.get_users("somthing_random")
        assert len(users) == 0
