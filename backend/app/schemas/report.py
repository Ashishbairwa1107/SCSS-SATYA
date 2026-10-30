from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    report_format: str = "PDF"  # "PDF" or "JSON"
    include_sensitive_gps: bool = False
    custom_notes: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    examination_id: str
    report_format: str
    file_size_bytes: int
    sha256_hash: str
    download_url: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
