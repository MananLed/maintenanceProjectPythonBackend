import pytest 
from fastapi.testclient import TestClient 
from app import app 


@pytest.fixture(scope="session")
def client():
    return TestClient(app)

 