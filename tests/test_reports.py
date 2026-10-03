from app.schemas import ReportCreate
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.main import rate_limit

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



def test_moderator_reports_with_token(client, moderator_token):
    response = client.get(
        "/moderator/reports",
        headers={
            "Authorization": f"Bearer {moderator_token}"
        }
    )

    assert response.status_code == 200


def test_moderator_reports_without_token():
    response = client.get("/moderator/reports")

    assert response.status_code == 401



def test_change_report_status(client, moderator_token, report):
    case_code = report["case_code"]

    response = client.patch(
        f"/moderator/reports/{case_code}/status",
        headers={
            "Authorization": f"Bearer {moderator_token}"
        },
        json={
            "status": "UNDER_REVIEW",
            "message": "Report is being investigated."
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"



def test_invalid_status(client, moderator_token, report):
    case_code = report["case_code"]

    response = client.patch(
        f"/moderator/reports/{case_code}/status",
        headers={
            "Authorization": f"Bearer {moderator_token}"
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


def test_moderator_token(moderator_token):
    assert moderator_token


def test_report_fixture(report):
    assert "case_code" in report

def test_report_fixture(report):
    assert "case_code" in report


def test_filter_by_category(client, moderator_token, report):
    response = client.get(
        "/moderator/reports?category=Security",
        headers={
            "Authorization": f"Bearer {moderator_token}"
        }
    )

    assert response.status_code == 200

    for item in response.json():
        assert item["category"] == "Security"


def test_filter_by_status(client, moderator_token, report):
    response = client.get(
        "/moderator/reports?status=SUBMITTED",
        headers={
            "Authorization": f"Bearer {moderator_token}"
        }
    )

    assert response.status_code == 200

    for item in response.json():
        assert item["status"] == "SUBMITTED"


def test_filter_by_category_and_status(client, moderator_token, report):
    response = client.get(
        "/moderator/reports?category=Security&status=SUBMITTED",
        headers={
            "Authorization": f"Bearer {moderator_token}"
        }
    )

    assert response.status_code == 200

    for item in response.json():
        assert item["category"] == "Security"
        assert item["status"] == "SUBMITTED"


def test_invalid_category_filter(client, moderator_token):
    response = client.get(
        "/moderator/reports?category=Random",
        headers={
            "Authorization": f"Bearer {moderator_token}"
        }
    )

    assert response.status_code == 422


def test_report_rate_limit(client):
    rate_limit.clear()

    data = {
        "category": "Security",
        "description": "Testing rate limit protection."
    }

    for _ in range(5):
        response = client.post("/reports", json=data)
        assert response.status_code == 200

    response = client.post("/reports", json=data)

    assert response.status_code == 429