# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app
import pytest

@pytest.mark.order(0) # global scope
def test_connect_to_db():
    with TestClient(app): # Will run with lifecycle function
        assert True
