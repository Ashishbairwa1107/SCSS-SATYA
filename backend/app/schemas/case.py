from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class CaseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    case_reference: Optional[str] = Field(None, max_length=100)
    purpose: Optional[str] = Field(None, max_length=255)
    evidence_source: Optional[str] = Field(None, max_length=255)
    investigator: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class CaseResponse(CaseBase):
    id: str
    case_reference: str
    created_at: datetime
    updated_at: datetime
    evidence_count: int = 0
    examination_count: int = 0

    model_config = ConfigDict(from_attributes=True)
