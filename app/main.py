from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report, StatusUpdate, Moderator
from app.schemas import (
    ReportCreate,
    ReportResponse,
    StatusUpdateCreate,
    ModeratorLogin
)
from app.auth import verify_password, create_access_token

import secrets



app = FastAPI(title="WhistleDrop")


@app.get("/")
def home():
    return {"message": "WhistleDrop API is running"}


@app.post("/reports")
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


@app.get("/reports/{case_code}", response_model=ReportResponse)
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

@app.post("/reports/{case_code}/updates")
def add_status_update(
    case_code: str,
    update: StatusUpdateCreate,
    db: Session = Depends(get_db)
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


@app.post("/moderator/login")
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


