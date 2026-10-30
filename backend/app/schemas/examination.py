from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.schemas.evidence import EvidenceResponse
from app.schemas.case import CaseResponse
from app.schemas.analysis import FindingResponse, ELAResponse, RGBStatisticsResponse, SpatialNoiseResponse
from app.schemas.review import ExaminerReviewResponse

class FindingsSummary(BaseModel):
    no_indicator_count: int = 0
    indicator_observed_count: int = 0
    inconclusive_count: int = 0
    total_findings: int = 0

class ExaminationResponse(BaseModel):
    id: str
    case_id: str
    evidence_id: str
    status: str
    failure_reason: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    case_reference: Optional[str] = None
    case_title: Optional[str] = None
    original_filename: Optional[str] = None
    detected_format: Optional[str] = None
    sha256_hash: Optional[str] = None
    review_status: Optional[str] = None
    integrity_status: Optional[str] = None
    findings_summary: Optional[FindingsSummary] = None

    model_config = ConfigDict(from_attributes=True)

class ExaminationDetailResponse(BaseModel):
    id: str
    case_id: str
    evidence_id: str
    status: str
    failure_reason: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    case: CaseResponse
    evidence: EvidenceResponse
    findings: list[FindingResponse] = []
    review: Optional[ExaminerReviewResponse] = None
    findings_summary: FindingsSummary
    has_ela: bool = False
    has_statistics: bool = False

    model_config = ConfigDict(from_attributes=True)
