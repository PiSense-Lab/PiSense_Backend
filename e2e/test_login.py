# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import USER_ROLES, User, Database, Authenticator
from datetime import timedelta
import pytest

@pytest.mark.order(1) # global scope
def test_create_get_users():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        auth = Authenticator()

        username = "test_username"
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

        out = auth.authenticate_user("test_username", password)
        assert isinstance(out, User)

        access_token = auth.create_access_token({"sub": user.username}, expires_delta=timedelta(minutes=int(Authenticator().ACCESS_TOKEN_EXPIRE_MINUTES)))
        assert not isinstance(access_token, type(None))

        token = access_token["access_token"]
        token_type = access_token["token_type"]

        assert not isinstance(token, type(None))
        assert token_type == "bearer"

        verify_out = auth.verify_token(token)
        print(verify_out)
        print(type(verify_out))

        assert 0 == 1