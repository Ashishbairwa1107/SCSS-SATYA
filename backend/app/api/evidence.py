import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.database.models import Evidence, IntegrityVerification, AnalysisResult, Examination
from app.schemas.evidence import EvidenceResponse, IntegrityVerificationResponse
from app.schemas.examination import ExaminationResponse
from app.services.storage import storage_service
from app.services.audit import log_audit_event
from app.core.config import settings
from app.core.constants import IntegrityStatus, AuditEventType
from app.core.security import validate_safe_path

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.post("", response_model=ExaminationResponse, status_code=status.HTTP_201_CREATED)
def register_evidence(
    file: UploadFile = File(...),
    case_title: Optional[str] = Form(None),
    case_reference: Optional[str] = Form(None),
    case_id: Optional[str] = Form(None),
    purpose: Optional[str] = Form(None),
    evidence_source: Optional[str] = Form(None),
    investigator: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Direct Evidence Registration endpoint (mirrors /api/examinations).
    Ingests evidence image, calculates cryptographic SHA-256 digest directly from uploaded bytes,
    preserves original bytes in isolated storage vault, and runs screening pipeline.
    """
    from app.api.examinations import create_examination
    return create_examination(
        file=file,
        case_title=case_title,
        case_reference=case_reference,
        case_id=case_id,
        purpose=purpose,
        evidence_source=evidence_source,
        investigator=investigator,
        notes=notes,
        db=db,
    )

@router.get("/artifacts/{filename}")
def get_artifact_file(filename: str):
    """Serve derived analysis artifacts (e.g. ELA heatmaps, preview exhibits)."""
    target = settings.ARTIFACTS_DIR / filename
    validated = validate_safe_path(target, settings.ARTIFACTS_DIR)

    if not validated.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact file not found.")

    # Determine media type
    ext = validated.suffix.lower()
    media_type = "image/png" if ext == ".png" else "application/octet-stream"
    return FileResponse(path=str(validated), media_type=media_type)

@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """Retrieve evidence record including format, dimensions, and cryptographic SHA-256 digest."""
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found.")

    latest_ver = db.query(IntegrityVerification).filter(
        IntegrityVerification.evidence_id == ev.id
    ).order_by(desc(IntegrityVerification.verified_at)).first()

    status_str = latest_ver.status if latest_ver else IntegrityStatus.UNVERIFIED.value

    return EvidenceResponse(
        id=ev.id,
        case_id=ev.case_id,
        original_filename=ev.original_filename,
        stored_filename=ev.stored_filename,
        file_size_bytes=ev.file_size_bytes,
        mime_type=ev.mime_type,
        detected_format=ev.detected_format,
        width=ev.width,
        height=ev.height,
        color_mode=ev.color_mode,
        sha256_hash=ev.sha256_hash,
        ingestion_timestamp=ev.ingestion_timestamp,
        is_specimen=ev.is_specimen,
        specimen_type=ev.specimen_type,
        integrity_status=status_str,
    )

@router.get("/{evidence_id}/original")
def download_original_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """
    Download unaltered pristine evidence bytes directly from the protected vault.
    Evidence bytes are preserved strictly as ingested.
    """
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found.")

    target_path = Path(ev.storage_path)
    validated = validate_safe_path(target_path, settings.VAULT_DIR)

    if not validated.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence file missing in vault.")

    return FileResponse(
        path=str(validated),
        filename=ev.original_filename,
        media_type=ev.mime_type or "application/octet-stream",
    )

@router.post("/{evidence_id}/verify", response_model=IntegrityVerificationResponse)
def verify_evidence_integrity(evidence_id: str, db: Session = Depends(get_db)):
    """
    Layer 2 — Tamper-Evident Evidence Integrity Verification.
    Re-reads stored evidence bytes directly from the vault and recomputes SHA-256.
    Compares against the immutable ingestion hash.
    """
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found.")

    is_match, recomputed = storage_service.verify_evidence_integrity(
        storage_path_str=ev.storage_path,
        expected_hash=ev.sha256_hash,
    )

    ver_status = IntegrityStatus.VERIFIED if is_match else IntegrityStatus.MISMATCH
    msg = (
        "Stored evidence bytes match the recorded ingestion hash."
        if is_match
        else "CRITICAL ALERT: Stored evidence bytes have been altered or corrupted! Hash mismatch detected."
    )

    ver_record = IntegrityVerification(
        evidence_id=ev.id,
        expected_hash=ev.sha256_hash,
        recomputed_hash=recomputed,
        status=ver_status.value,
        details=msg,
    )
    db.add(ver_record)
    db.commit()
    db.refresh(ver_record)

    log_audit_event(
        db,
        event_type=AuditEventType.INTEGRITY_VERIFIED if is_match else AuditEventType.INTEGRITY_FAILED,
        entity_type="Evidence",
        entity_id=ev.id,
        case_id=ev.case_id,
        details={
            "expected_hash": ev.sha256_hash,
            "recomputed_hash": recomputed,
            "match": is_match,
        }
    )

    return IntegrityVerificationResponse(
        evidence_id=ev.id,
        expected_hash=ev.sha256_hash,
        recomputed_hash=recomputed,
        status=ver_status.value,
        verified_at=ver_record.verified_at,
        details=ver_record.details,
        message=msg,
    )

@router.get("/{evidence_id}/metadata")
def get_evidence_metadata(evidence_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed EXIF/IPTC/TIFF container metadata inspection results."""
    ev = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not ev:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence item not found.")

    exam = db.query(Examination).filter(Examination.evidence_id == ev.id).first()
    if not exam or not exam.analysis_result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metadata analysis not available.")

    meta_str = exam.analysis_result.metadata_json
    if not meta_str:
        return {"categories": [], "summary": {}}
    return json.loads(meta_str)
