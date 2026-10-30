from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ChecklistItem(BaseModel):
    id: str
    label: str
    description: str
    checked: bool = False
    notes: Optional[str] = None

class ExaminerReviewUpdate(BaseModel):
    examiner_name: str = Field(..., min_length=1, max_length=100)
    organization: Optional[str] = Field(None, max_length=200)
    qualification: Optional[str] = Field(None, max_length=255)
    qualitative_notes: Optional[str] = None
    checklist_responses: list[ChecklistItem] = []
    review_status: str  # "Pending Review", "Under Review", "Reviewed — No Final Opinion", "Examiner Opinion Recorded"
    examiner_opinion: Optional[str] = None
    confirm_opinion_disclosure: bool = False

class ExaminerReviewResponse(BaseModel):
    id: str
    examination_id: str
    examiner_name: str
    organization: Optional[str] = None
    qualification: Optional[str] = None
    credential_status: str
    qualitative_notes: Optional[str] = None
    checklist_responses: list[ChecklistItem] = []
    review_status: str
    examiner_opinion: Optional[str] = None
    reviewed_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
