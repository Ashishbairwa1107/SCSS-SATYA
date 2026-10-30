from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
    doctrine: str
    database_connected: bool
    vault_accessible: bool

class DashboardMetrics(BaseModel):
    total_examinations: int
    total_evidence_items: int
    pending_human_reviews: int
    completed_examinations: int
    integrity_failures: int
    total_cases: int

class SystemInfoResponse(BaseModel):
    platform_name: str
    full_title: str
    version: str
    organization: str
    challenge: str
    sector: str
    sub_theme: str
    doctrine: str
    python_version: str
    storage_vault_path: str
    max_file_size_mb: int
    max_pixels: int
    supported_formats: list[str]
    disclaimer: str
