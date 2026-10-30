import sys
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.database.session import get_db
from app.core.config import settings
from app.database.models import Case, Evidence, Examination, ExaminerReview, IntegrityVerification
from app.schemas.system import HealthResponse, DashboardMetrics, SystemInfoResponse
from app.core.constants import ReviewStatus, IntegrityStatus, ExaminationStatus

router = APIRouter(prefix="", tags=["System"])

@router.get("/health", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)):
    """Health screening check verifying database connection and storage vault accessibility."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    vault_ok = settings.VAULT_DIR.exists() and settings.VAULT_DIR.is_dir()

    return HealthResponse(
        status="HEALTHY" if (db_ok and vault_ok) else "DEGRADED",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
        doctrine=settings.DOCTRINE,
        database_connected=db_ok,
        vault_accessible=vault_ok,
    )

@router.get("/system/info", response_model=SystemInfoResponse)
def get_system_info():
    """Retrieve platform technical specifications, parameters, and doctrine."""
    return SystemInfoResponse(
        platform_name=settings.PROJECT_NAME,
        full_title=settings.PROJECT_FULL_TITLE,
        version=settings.VERSION,
        organization=settings.ORGANIZATION,
        challenge=settings.CHALLENGE,
        sector=settings.SECTOR,
        sub_theme=settings.SUB_THEME,
        doctrine=settings.DOCTRINE,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        storage_vault_path="storage/vault (Isolated)",
        max_file_size_mb=settings.MAX_FILE_SIZE_BYTES // (1024 * 1024),
        max_pixels=settings.MAX_IMAGE_PIXELS,
        supported_formats=sorted(list(settings.SUPPORTED_FORMATS)),
        disclaimer=(
            "SCSS SATYA is a forensic screening and documentation prototype, not a certified forensic laboratory instrument. "
            "The tool screens. The expert decides."
        ),
    )

@router.get("/system/metrics", response_model=DashboardMetrics)
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Retrieve real database-backed platform metrics for forensic dashboard."""
    total_cases = db.query(func.count(Case.id)).scalar() or 0
    total_evidence = db.query(func.count(Evidence.id)).scalar() or 0
    total_examinations = db.query(func.count(Examination.id)).scalar() or 0
    completed_examinations = db.query(func.count(Examination.id)).filter(
        Examination.status == ExaminationStatus.COMPLETED.value
    ).scalar() or 0
    
    pending_reviews = db.query(func.count(ExaminerReview.id)).filter(
        ExaminerReview.review_status.in_([ReviewStatus.PENDING_REVIEW.value, ReviewStatus.UNDER_REVIEW.value])
    ).scalar() or 0

    integrity_failures = db.query(func.count(IntegrityVerification.id)).filter(
        IntegrityVerification.status == IntegrityStatus.MISMATCH.value
    ).scalar() or 0

    return DashboardMetrics(
        total_examinations=total_examinations,
        total_evidence_items=total_evidence,
        pending_human_reviews=pending_reviews,
        completed_examinations=completed_examinations,
        integrity_failures=integrity_failures,
        total_cases=total_cases,
    )
