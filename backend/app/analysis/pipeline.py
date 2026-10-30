import io
import json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.constants import ExaminationStatus, AuditEventType, ReviewStatus, STANDARD_VERIFICATION_CHECKLIST
from app.database.models import Evidence, Examination, AnalysisResult, Finding, ExaminerReview
from app.analysis.metadata import extract_image_metadata
from app.analysis.ela import perform_error_level_analysis
from app.analysis.image_statistics import calculate_image_statistics
from app.analysis.findings import generate_explainable_findings
from app.services.audit import log_audit_event

def run_screening_pipeline(db: Session, examination_id: str) -> Examination:
    """
    Execute the Four-Layer Forensic Screening Pipeline.
    Layer 1: Passive Image Screening (Metadata, ELA, Geometry & Statistics)
    Layer 2: Tamper-Evident SHA-256 Record
    Layer 3: Explainable Technical Findings
    Layer 4: Qualified Human Forensic Review Initializer
    """
    exam = db.query(Examination).filter(Examination.id == examination_id).first()
    if not exam:
        raise ValueError(f"Examination {examination_id} not found.")

    evidence = db.query(Evidence).filter(Evidence.id == exam.evidence_id).first()
    if not evidence:
        raise ValueError(f"Evidence {exam.evidence_id} not found.")

    exam.status = ExaminationStatus.PROCESSING.value
    db.commit()

    log_audit_event(
        db,
        event_type=AuditEventType.EXAMINATION_STARTED,
        entity_type="Examination",
        entity_id=exam.id,
        case_id=exam.case_id,
        details={"evidence_id": evidence.id, "sha256": evidence.sha256_hash}
    )

    try:
        # Read pristine evidence bytes from protected vault
        with open(evidence.storage_path, "rb") as f:
            evidence_bytes = f.read()

        # 1. Metadata Inspection
        metadata_res = extract_image_metadata(evidence_bytes, evidence.original_filename)

        # 2. Error Level Analysis (JPEG only; honest alternative handling for PNG/lossless)
        ela_res = perform_error_level_analysis(
            evidence_bytes,
            detected_format=evidence.detected_format,
            quality=settings.ELA_JPEG_QUALITY,
            scale=settings.ELA_AMPLIFICATION_SCALE,
        )

        # 3. Geometry and Spatial Noise Statistics
        stats_res = calculate_image_statistics(evidence_bytes)

        # 4. Synthesize Explainable Findings
        findings_data = generate_explainable_findings(
            metadata_result=metadata_res,
            ela_result=ela_res,
            stats_result=stats_res,
            detected_format=evidence.detected_format,
        )

        # Persist Analysis Result
        analysis_record = AnalysisResult(
            examination_id=exam.id,
            metadata_json=json.dumps(metadata_res),
            ela_artifact_path=ela_res.get("artifact_id"),
            ela_scale=ela_res.get("scale"),
            ela_quality=ela_res.get("quality"),
            ela_format_supported=ela_res.get("format_supported", False),
            ela_notes=ela_res.get("notes"),
            rgb_statistics_json=json.dumps(stats_res.get("rgb_statistics")),
            spatial_noise_json=json.dumps(stats_res.get("spatial_noise")),
            calculated_at=datetime.now(timezone.utc),
        )
        db.add(analysis_record)

        # Persist Structured Findings
        for f_data in findings_data:
            finding_record = Finding(
                examination_id=exam.id,
                finding_key=f_data["finding_key"],
                indicator_name=f_data["indicator_name"],
                status=f_data["status"],
                observed_evidence=f_data["observed_evidence"],
                explanation=f_data["explanation"],
                significance=f_data["significance"],
                limitations=f_data["limitations"],
                recommended_action=f_data["recommended_action"],
                order_index=f_data["order_index"],
            )
            db.add(finding_record)

        # Initialize Layer 4: Examiner Review record if not already present
        existing_review = db.query(ExaminerReview).filter(ExaminerReview.examination_id == exam.id).first()
        if not existing_review:
            initial_checklist = [
                {**item, "checked": False, "notes": ""}
                for item in STANDARD_VERIFICATION_CHECKLIST
            ]
            review_record = ExaminerReview(
                examination_id=exam.id,
                examiner_name="Unassigned Examiner",
                organization=settings.ORGANIZATION,
                qualification="Pending Assignment",
                credential_status="UNVERIFIED",
                qualitative_notes=None,
                checklist_responses_json=json.dumps(initial_checklist),
                review_status=ReviewStatus.PENDING_REVIEW.value,
                examiner_opinion=None,
            )
            db.add(review_record)

        # Update Examination status
        exam.status = ExaminationStatus.COMPLETED.value
        exam.completed_at = datetime.now(timezone.utc)
        db.commit()

        log_audit_event(
            db,
            event_type=AuditEventType.EXAMINATION_COMPLETED,
            entity_type="Examination",
            entity_id=exam.id,
            case_id=exam.case_id,
            details={"findings_count": len(findings_data), "status": exam.status}
        )

        return exam

    except Exception as exc:
        db.rollback()
        exam.status = ExaminationStatus.FAILED.value
        exam.failure_reason = str(exc)
        exam.completed_at = datetime.now(timezone.utc)
        db.commit()

        log_audit_event(
            db,
            event_type=AuditEventType.EXAMINATION_FAILED,
            entity_type="Examination",
            entity_id=exam.id,
            case_id=exam.case_id,
            details={"error": str(exc)}
        )
        return exam
