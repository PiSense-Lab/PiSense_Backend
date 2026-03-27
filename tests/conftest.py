import pytest
from fastapi.testclient import TestClient
from pisense.api.main import app  # make sure this import is correct

@pytest.fixture
def client():
    return TestClient(app)