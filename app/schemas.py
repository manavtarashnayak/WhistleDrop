from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field
from typing import Literal

class ReportCreate(BaseModel):
    category: Literal[
        "Security",
        "Harassment",
        "Corruption",
        "Technical",
        "Other"
    ]
    description: str = Field(min_length=10)
    evidence_url: HttpUrl | None = None


class StatusUpdateResponse(BaseModel):
    message: str
    created_at: datetime


class ReportResponse(BaseModel):
    case_code: str
    category: str
    status: str
    created_at: datetime
    updates: list[StatusUpdateResponse]

class StatusUpdateCreate(BaseModel):
    message: str

class ModeratorLogin(BaseModel):
    username: str
    password: str

class StatusChange(BaseModel):
    status: Literal[
        "SUBMITTED",
        "UNDER_REVIEW",
        "RESOLVED",
        "DISMISSED"
    ]
    message: str = Field(min_length=1)