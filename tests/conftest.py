import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def moderator_token(client):
    response = client.post(
        "/moderator/login",
        json={
            "username": "admin",
            "password": "Whistle@123"
        }
    )

    return response.json()["access_token"]


@pytest.fixture
def report(client):
    response = client.post(
        "/reports",
        json={
            "category": "Security",
            "description": "Test report for automated testing."
        }
    )

    return response.json()

