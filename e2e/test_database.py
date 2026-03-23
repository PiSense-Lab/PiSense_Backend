# import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app

def test_connect_to_db():
    with TestClient(app): # Will run with lifecycle function
        assert True
