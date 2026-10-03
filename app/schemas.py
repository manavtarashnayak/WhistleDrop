from datetime import datetime

from pydantic import BaseModel, HttpUrl, Field

from typing import Literal


Category = Literal[
    "Security",
    "Harassment",
    "Corruption",
    "Technical",
    "Other"
]

Status = Literal[
    "SUBMITTED",
    "UNDER_REVIEW",
    "RESOLVED",
    "DISMISSED"
]


class ReportCreate(BaseModel):
    category: Category
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
    status: Status
    message: str = Field(min_length=1)