import uuid
from PIL import Image
import io
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Case, Evidence, Examination, IntegrityVerification
from app.schemas.examination import ExaminationResponse, FindingsSummary
from app.services.storage import storage_service
from app.services.audit import log_audit_event
from app.services.specimens import (
    generate_specimen_a_camera_photo,
    generate_specimen_b_spliced_composite,
    generate_specimen_c_lossless_png,
)
from app.analysis.pipeline import run_screening_pipeline
from app.core.constants import AuditEventType, IntegrityStatus, ExaminationStatus, FindingStatus
from app.database.models import Finding

router = APIRouter(prefix="/specimens", tags=["Demonstration Specimens"])

def register_and_screen_specimen(
    db: Session,
    specimen_bytes: bytes,
    filename: str,
    specimen_type: str,
    specimen_title: str,
    purpose_desc: str,
) -> ExaminationResponse:
    """Helper to register and execute pipeline for calibrated demonstration specimens."""
    
    # Store original specimen bytes
    stored_filename, storage_path, file_size, sha256_hash = storage_service.save_evidence_bytes(
        data=specimen_bytes,
        original_filename=filename,
    )

    # Determine image dimensions & format
    with Image.open(io.BytesIO(specimen_bytes)) as img:
        detected_format = img.format or "UNKNOWN"
        width, height = img.size
        color_mode = img.mode

    # Dedicated Case clearly labeled as demonstration specimen
    case_ref = f"SPEC-{uuid.uuid4().hex[:6].upper()}"
    case = Case(
        case_reference=case_ref,
        title=f"[DEMO SPECIMEN] {specimen_title}",
        purpose=purpose_desc,
        evidence_source="Calibrated Synthetic Specimen Generator",
        investigator="Automated Calibration Engine",
        notes="Synthetic Demonstration Specimen — Not Real Case Evidence. Ground truth recipe maintained separately.",
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # Evidence record with is_specimen=True
    evidence = Evidence(
        case_id=case.id,
        original_filename=filename,
        stored_filename=stored_filename,
        file_size_bytes=file_size,
        mime_type=f"image/{detected_format.lower()}",
        detected_format=detected_format,
        width=width,
        height=height,
        color_mode=color_mode,
        sha256_hash=sha256_hash,
        storage_path=storage_path,
        is_specimen=True,
        specimen_type=specimen_type,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # Initial integrity record
    init_ver = IntegrityVerification(
        evidence_id=evidence.id,
        expected_hash=sha256_hash,
        recomputed_hash=sha256_hash,
        status=IntegrityStatus.VERIFIED.value,
        details="Specimen baseline SHA-256 registered.",
    )
    db.add(init_ver)

    log_audit_event(
        db,
        event_type=AuditEventType.SPECIMEN_GENERATED,
        entity_type="Evidence",
        entity_id=evidence.id,
        case_id=case.id,
        details={"specimen_type": specimen_type, "sha256": sha256_hash}
    )

    # Examination
    examination = Examination(
        case_id=case.id,
        evidence_id=evidence.id,
        status=ExaminationStatus.PENDING.value,
    )
    db.add(examination)
    db.commit()
    db.refresh(examination)

    # Run screening pipeline
    run_screening_pipeline(db, examination.id)
    db.refresh(examination)

    findings = db.query(Finding).filter(Finding.examination_id == examination.id).all()
    no_ind = sum(1 for f in findings if f.status == FindingStatus.NO_INDICATOR.value)
    ind_obs = sum(1 for f in findings if f.status == FindingStatus.INDICATOR_OBSERVED.value)
    inconcl = sum(1 for f in findings if f.status == FindingStatus.INCONCLUSIVE.value)

    return ExaminationResponse(
        id=examination.id,
        case_id=case.id,
        evidence_id=evidence.id,
        status=examination.status,
        failure_reason=examination.failure_reason,
        started_at=examination.started_at,
        completed_at=examination.completed_at,
        case_reference=case.case_reference,
        case_title=case.title,
        original_filename=evidence.original_filename,
        detected_format=evidence.detected_format,
        sha256_hash=evidence.sha256_hash,
        review_status="Pending Review",
        integrity_status=IntegrityStatus.VERIFIED.value,
        findings_summary=FindingsSummary(
            no_indicator_count=no_ind,
            indicator_observed_count=ind_obs,
            inconclusive_count=inconcl,
            total_findings=len(findings),
        )
    )

@router.post("/camera-style", response_model=ExaminationResponse, status_code=status.HTTP_201_CREATED)
def create_camera_style_specimen(db: Session = Depends(get_db)):
    """Generate Specimen A: Natural landscape photograph with synthetic camera EXIF metadata."""
    data_bytes, filename, recipe = generate_specimen_a_camera_photo()
    return register_and_screen_specimen(
        db=db,
        specimen_bytes=data_bytes,
        filename=filename,
        specimen_type="camera_style",
        specimen_title="Camera-Style Landscape (Specimen A)",
        purpose_desc="Calibration benchmark for nominal camera-style metadata and homogeneous ELA residuals.",
    )

@router.post("/spliced-composite", response_model=ExaminationResponse, status_code=status.HTTP_201_CREATED)
def create_spliced_composite_specimen(db: Session = Depends(get_db)):
    """Generate Specimen B: Spliced composite with differing recompression residuals and software tag."""
    data_bytes, filename, recipe = generate_specimen_b_spliced_composite()
    return register_and_screen_specimen(
        db=db,
        specimen_bytes=data_bytes,
        filename=filename,
        specimen_type="spliced_composite",
        specimen_title="Spliced Structural Composite (Specimen B)",
        purpose_desc="Demonstration specimen containing inserted badge with divergent recompression error and GIMP software tag.",
    )

@router.post("/lossless-png", response_model=ExaminationResponse, status_code=status.HTTP_201_CREATED)
def create_lossless_png_specimen(db: Session = Depends(get_db)):
    """Generate Specimen C: Lossless calibration target to demonstrate honest JPEG ELA unavailability."""
    data_bytes, filename, recipe = generate_specimen_c_lossless_png()
    return register_and_screen_specimen(
        db=db,
        specimen_bytes=data_bytes,
        filename=filename,
        specimen_type="lossless_png",
        specimen_title="Lossless Target Chart (Specimen C)",
        purpose_desc="Demonstrates lossless PNG handling: successful hashing and RGB statistics with explicit JPEG ELA rejection.",
    )
