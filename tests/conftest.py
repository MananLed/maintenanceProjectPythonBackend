import pytest 
from fastapi.testclient import TestClient 
from fastapi import Request 
from internal.utils.jwt import verify_jwt
from app import app 
import uuid
from internal.constants.constants import *

@pytest.fixture(scope="session")
def client():
    return TestClient(app, raise_server_exceptions=False)

@pytest.fixture
def override_jwt():
    def _override(role="resident", user_id=None, email="test@example.com"):
        if user_id is None:
            user_id = str(uuid.uuid4())

        def fake_verify_jwt(request: Request):
            request.state.user = {
                "email": email,
                "role": role,
                "user_id": user_id,
            }

        app.dependency_overrides[verify_jwt] = fake_verify_jwt

    yield _override
    app.dependency_overrides.clear()