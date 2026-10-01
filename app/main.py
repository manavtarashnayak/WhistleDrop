from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report
from app.schemas import ReportCreate

app = FastAPI(title="WhistleDrop")


@app.get("/")
def home():
    return {"message": "WhistleDrop API is running"}


@app.post("/reports")
def create_report(report: ReportCreate, db: Session = Depends(get_db)):

    new_report = Report(
        case_code="TEST123",
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