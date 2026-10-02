from datetime import datetime
from pydantic import BaseModel, HttpUrl


class ReportCreate(BaseModel):
    category: str
    description: str
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
    status: str
    message: str