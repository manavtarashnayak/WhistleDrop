from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report, StatusUpdate, Moderator
from app.schemas import (
    ReportCreate,
    ReportResponse,
    StatusUpdateCreate,
    ModeratorLogin,
    StatusChange,
    Category,
    Status
)
from app.auth import verify_password, create_access_token, get_current_moderator
from sqlalchemy.exc import SQLAlchemyError
import secrets



app = FastAPI(
    title="WhistleDrop API",
    description="Anonymous confidential reporting system",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"message": "WhistleDrop API is running"}


@app.post(
    "/reports",
    tags=["Reports"],
    summary="Create a new report",
    description="Submit an anonymous confidential report."
)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):

    new_report = Report(
        case_code=secrets.token_urlsafe(12),
        category=report.category,
        description=report.description,
        evidence_url=str(report.evidence_url) if report.evidence_url else None
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return {
        "message": "Report submitted successfully",
        "case_code": new_report.case_code
    }


@app.get(
    "/reports/{case_code}",
    tags=["Reports"],
    summary="Get report status",
    description="Track a submitted report using its case code."
)
def get_report(case_code: str, db: Session = Depends(get_db)):

    report = db.query(Report).filter(
        Report.case_code == case_code
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Invalid case code"
        )

    return {
        "case_code": report.case_code,
        "category": report.category,
        "status": report.status,
        "created_at": report.created_at,
        "updates": [
            {
                "message": update.message,
                "created_at": update.created_at
            }
            for update in report.status_updates
        ]
    }



@app.post(
    "/moderator/login",
    tags=["Moderator"],
    summary="Moderator login",
    description="Authenticate a moderator and receive a JWT access token."
)
def moderator_login(
    login: ModeratorLogin,
    db: Session = Depends(get_db)
):
    moderator = db.query(Moderator).filter(
        Moderator.username == login.username
    ).first()

    if not moderator:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        login.password,
        moderator.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(moderator.username)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get(
    "/moderator/reports",
    tags=["Moderator"],
    summary="Get reports",
    description="View all reports or filter them by category and status.",
    responses={
        200: {"description": "Reports retrieved successfully"},
        401: {"description": "Invalid or expired token"},
        422: {"description": "Invalid category or status filter"}
    }
)
def get_all_reports(
    category: Category | None = None,
    status: Status | None = None,
    db: Session = Depends(get_db),
    current_moderator: Moderator = Depends(get_current_moderator)
):
    query = db.query(Report)

    if category:
        query = query.filter(Report.category == category)

    if status:
        query = query.filter(Report.status == status)

    reports = query.all()

    return reports


@app.patch(
    "/moderator/reports/{case_code}/status",
    tags=["Moderator"],
    summary="Change report status",
    description="Update the status of a report. Moderator authentication required."
)
def change_status(
    case_code: str,
    data: StatusChange,
    db: Session = Depends(get_db),
    moderator: str = Depends(get_current_moderator)
):
    report = db.query(Report).filter(
        Report.case_code == case_code
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Invalid case code"
        )

    allowed_statuses = [
        "SUBMITTED",
        "UNDER_REVIEW",
        "RESOLVED",
        "DISMISSED"
    ]

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid status"
        )

    try:
        report.status = data.status

        new_update = StatusUpdate(
            report_id=report.id,
            message=data.message
        )

        db.add(new_update)
        db.commit()
        db.refresh(report)
    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unable to update report"
        )

    return {
        "message": "Report status updated successfully",
        "status": report.status
    }



@app.post(
    "/reports/{case_code}/updates",
    tags=["Moderator"],
    summary="Add status update",
    description="Add an update to a report. Moderator authentication required."
)
def add_status_update(
    case_code: str,
    update: StatusUpdateCreate,
    db: Session = Depends(get_db),
    moderator: str = Depends(get_current_moderator)
):

    report = db.query(Report).filter(
        Report.case_code == case_code
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Invalid case code"
        )

    new_update = StatusUpdate(
        report_id=report.id,
        message=update.message
    )

    db.add(new_update)
    db.commit()
    db.refresh(new_update)

    return {
        "message": "Status update added successfully"
    }

