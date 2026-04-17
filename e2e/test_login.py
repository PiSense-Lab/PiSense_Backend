# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
from pisense.backend.classes import User, Database, Authenticator
from datetime import timedelta
import pytest

@pytest.mark.order(1) # global scope
def test_user_login():
    with TestClient(app): # Will run with lifecycle function
        db = Database()
        auth = Authenticator()

        username = "test_username"
        email = "blank@email.com"
        password = "defnitly_hashed"

        user = db.create_user(username=username, email=email, password=password)
        print("User object from `create_user`")
        print(user)
        assert isinstance(user, User)
        assert user.username == username
        assert user.email == email

        out = auth.authenticate_user("test_username", password)
        assert isinstance(out, User)

        token = auth.create_access_token({"sub": user.username})
        assert isinstance(token, str)

        verify_out = auth.verify_token(token)
        print(verify_out)
        print(type(verify_out))

        assert isinstance(verify_out, dict)
        assert verify_out["sub"] == username
        assert isinstance(verify_out["exp"], int)
        short_expire = verify_out["exp"]

        long_token = auth.create_access_token({"sub": user.username}, expires_delta=timedelta(days=int(Authenticator().PISENSE_AUTH_ACCESS_TOKEN_REMEMBER_ME_DAYS)))

        assert isinstance(long_token, str)

        verify_out_long = auth.verify_token(long_token)
        print(verify_out_long)
        print(type(verify_out_long))

        assert isinstance(verify_out_long, dict)
        assert verify_out_long["sub"] == username
        assert isinstance(verify_out_long["exp"], int)
        long_expire = verify_out_long["exp"]

        assert long_expire > short_expire
