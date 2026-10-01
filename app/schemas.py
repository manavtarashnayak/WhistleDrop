from pydantic import BaseModel, HttpUrl


class ReportCreate(BaseModel):
    category: str
    description: str
    evidence_url: HttpUrl | None = None