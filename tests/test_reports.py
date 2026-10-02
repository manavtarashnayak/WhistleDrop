from app.schemas import ReportCreate
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_valid_report():
    report = ReportCreate(
        category="Security",
        description="There is a security issue."
    )

    assert report.category == "Security"


def test_invalid_category():
    with pytest.raises(ValueError):
        ReportCreate(
            category="Random",
            description="There is a security issue."
        )

def test_short_description():
    with pytest.raises(ValueError):
        ReportCreate(
            category="Security",
            description="Help"
        )


def test_create_report():
    response = client.post(
        "/reports",
        json={
            "category": "Security",
            "description": "There is a security issue."
        }
    )

def test_create_report():
    response = client.post(
        "/reports",
        json={
            "category": "Security",
            "description": "There is a security issue."
        }
    )

    assert response.status_code == 200


def test_create_report_invalid_category():
    response = client.post(
        "/reports",
        json={
            "category": "Random",
            "description": "There is a security issue."
        }
    )

    assert response.status_code == 422


def test_invalid_case_code():
    response = client.get(
        "/reports/does-not-exist"
    )

    assert response.status_code == 404


def test_moderator_login():
    response = client.post(
        "/moderator/login",
        json={
            "username": "admin",
            "password": "Whistle@123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_moderator_login_wrong_password():
    response = client.post(
        "/moderator/login",
        json={
            "username": "admin",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401



def test_moderator_reports_with_token():
    login_response = client.post(
        "/moderator/login",
        json={
            "username": "admin",
            "password": "Whistle@123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/moderator/reports",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200


def test_moderator_reports_without_token():
    response = client.get("/moderator/reports")

    assert response.status_code == 401


def test_change_report_status():
    report_response = client.post(
        "/reports",
        json={
            "category": "Security",
            "description": "Testing status change."
        }
    )

    assert report_response.status_code == 200

    case_code = report_response.json()["case_code"]

    login_response = client.post(
        "/moderator/login",
        json={
            "username": "admin",
            "password": "Whistle@123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        f"/moderator/reports/{case_code}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "UNDER_REVIEW",
            "message": "Report is being investigated."
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"


def test_invalid_status():
    report_response = client.post(
        "/reports",
        json={
            "category": "Security",
            "description": "Testing invalid status."
        }
    )

    assert report_response.status_code == 200

    case_code = report_response.json()["case_code"]

    login_response = client.post(
        "/moderator/login",
        json={
            "username": "admin",
            "password": "Whistle@123"
        }
    )

    token = login_response.json()["access_token"]

    response = client.patch(
        f"/moderator/reports/{case_code}/status",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "status": "RANDOM_STATUS",
            "message": "Testing invalid status."
        }
    )

    assert response.status_code == 422


def test_change_status_without_token():
    report_response = client.post(
        "/reports",
        json={
            "category": "Security",
            "description": "Testing unauthorized status change."
        }
    )

    assert report_response.status_code == 200

    case_code = report_response.json()["case_code"]

    response = client.patch(
        f"/moderator/reports/{case_code}/status",
        json={
            "status": "UNDER_REVIEW",
            "message": "Unauthorized test."
        }
    )

    assert response.status_code == 401