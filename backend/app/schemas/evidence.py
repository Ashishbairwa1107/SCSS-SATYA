from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class EvidenceResponse(BaseModel):
    id: str
    case_id: str
    original_filename: str
    stored_filename: str
    file_size_bytes: int
    mime_type: str
    detected_format: str
    width: Optional[int] = None
    height: Optional[int] = None
    color_mode: Optional[str] = None
    sha256_hash: str
    ingestion_timestamp: datetime
    is_specimen: bool = False
    specimen_type: Optional[str] = None
    integrity_status: Optional[str] = "UNVERIFIED"

    model_config = ConfigDict(from_attributes=True)

class IntegrityVerificationResponse(BaseModel):
    evidence_id: str
    expected_hash: str
    recomputed_hash: str
    status: str
    verified_at: datetime
    details: str
    message: str

    model_config = ConfigDict(from_attributes=True)
