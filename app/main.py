from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.database import get_db
from app.models import Report
from app.schemas import ReportCreate
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


@app.get("/reports/{case_code}")
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
        "created_at": report.created_at
    }