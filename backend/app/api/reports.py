import json
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.database.models import Examination, GeneratedReport, Finding, Case, Evidence, ExaminerReview, AnalysisResult
from app.schemas.report import ReportCreate, ReportResponse
from app.services.storage import storage_service
from app.services.audit import log_audit_event
from app.reports.pdf_report import build_pdf_report
from app.reports.json_report import build_json_report
from app.core.config import settings
from app.core.constants import AuditEventType
from app.core.security import validate_safe_path

router = APIRouter(prefix="", tags=["Reports"])

@router.post("/examinations/{examination_id}/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def generate_report(
    examination_id: str,
    report_in: ReportCreate,
    db: Session = Depends(get_db)
):
    """
    Generate an official forensic screening report in PDF or JSON format.
    Calculates SHA-256 hash of report bytes, persists into storage/reports, and records audit event.
    """
    ex = db.query(Examination).filter(Examination.id == examination_id).first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examination not found.")

    case = ex.case
    evidence = ex.evidence
    findings = db.query(Finding).filter(Finding.examination_id == ex.id).order_by(Finding.order_index).all()
    review = ex.review
    analysis = ex.analysis_result

    report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
    fmt = report_in.report_format.upper()

    case_dict = {
        "id": case.id,
        "case_reference": case.case_reference,
        "title": case.title,
        "purpose": case.purpose,
        "evidence_source": case.evidence_source,
        "investigator": case.investigator,
        "notes": case.notes,
        "created_at": case.created_at,
    }
    evidence_dict = {
        "id": evidence.id,
        "original_filename": evidence.original_filename,
        "stored_filename": evidence.stored_filename,
        "file_size_bytes": evidence.file_size_bytes,
        "detected_format": evidence.detected_format,
        "width": evidence.width,
        "height": evidence.height,
        "color_mode": evidence.color_mode,
        "sha256_hash": evidence.sha256_hash,
        "ingestion_timestamp": evidence.ingestion_timestamp,
        "is_specimen": evidence.is_specimen,
        "specimen_type": evidence.specimen_type,
    }
    exam_dict = {
        "id": ex.id,
        "status": ex.status,
        "started_at": ex.started_at,
        "completed_at": ex.completed_at,
        "failure_reason": ex.failure_reason,
    }
    analysis_dict = {
        "metadata_json": analysis.metadata_json if analysis else None,
        "ela_artifact_path": analysis.ela_artifact_path if analysis else None,
        "ela_scale": analysis.ela_scale if analysis else None,
        "ela_quality": analysis.ela_quality if analysis else None,
        "ela_format_supported": analysis.ela_format_supported if analysis else False,
        "ela_notes": analysis.ela_notes if analysis else None,
        "rgb_statistics_json": analysis.rgb_statistics_json if analysis else None,
        "spatial_noise_json": analysis.spatial_noise_json if analysis else None,
    }
    findings_list = [
        {
            "id": f.id,
            "finding_key": f.finding_key,
            "indicator_name": f.indicator_name,
            "status": f.status,
            "observed_evidence": f.observed_evidence,
            "explanation": f.explanation,
            "significance": f.significance,
            "limitations": f.limitations,
            "recommended_action": f.recommended_action,
            "order_index": f.order_index,
        } for f in findings
    ]
    review_dict = {
        "examiner_name": review.examiner_name if review else "Unassigned",
        "organization": review.organization if review else settings.ORGANIZATION,
        "qualification": review.qualification if review else "Pending Assignment",
        "credential_status": review.credential_status if review else "UNVERIFIED",
        "qualitative_notes": review.qualitative_notes if review else None,
        "checklist_responses_json": review.checklist_responses_json if review else None,
        "review_status": review.review_status if review else "Pending Review",
        "examiner_opinion": review.examiner_opinion if review else None,
        "reviewed_at": review.reviewed_at if review else None,
    }

    if fmt == "PDF":
        report_bytes = build_pdf_report(
            case_data=case_dict,
            evidence_data=evidence_dict,
            examination_data=exam_dict,
            analysis_data=analysis_dict,
            findings_data=findings_list,
            review_data=review_dict,
            report_id=report_id,
        )
        ext = ".pdf"
    elif fmt == "JSON":
        json_obj = build_json_report(
            case_data=case_dict,
            evidence_data=evidence_dict,
            examination_data=exam_dict,
            analysis_data=analysis_dict,
            findings_data=findings_list,
            review_data=review_dict,
            report_id=report_id,
        )
        report_bytes = json.dumps(json_obj, indent=2).encode("utf-8")
        ext = ".json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported report format '{fmt}'. Choose 'PDF' or 'JSON'."
        )

    # Save report
    rep_filename, rep_path, file_size, rep_sha256 = storage_service.save_report(
        data=report_bytes,
        extension=ext,
        prefix=f"report_{fmt.lower()}",
    )

    # Persist database record
    rep_record = GeneratedReport(
        examination_id=ex.id,
        report_format=fmt,
        file_path=rep_path,
        file_size_bytes=file_size,
        sha256_hash=rep_sha256,
    )
    db.add(rep_record)
    db.commit()
    db.refresh(rep_record)

    log_audit_event(
        db,
        event_type=AuditEventType.REPORT_GENERATED,
        entity_type="GeneratedReport",
        entity_id=rep_record.id,
        case_id=case.id,
        details={
            "report_id": report_id,
            "format": fmt,
            "sha256": rep_sha256,
            "file_size": file_size,
        }
    )

    download_endpoint = f"/api/reports/{rep_record.id}/{fmt.lower()}"

    return ReportResponse(
        id=rep_record.id,
        examination_id=ex.id,
        report_format=fmt,
        file_size_bytes=file_size,
        sha256_hash=rep_sha256,
        download_url=download_endpoint,
        generated_at=rep_record.generated_at,
    )

@router.get("/examinations/{examination_id}/reports", response_model=list[ReportResponse])
def list_reports(examination_id: str, db: Session = Depends(get_db)):
    """List all generated reports for an examination."""
    reports = db.query(GeneratedReport).filter(
        GeneratedReport.examination_id == examination_id
    ).order_by(desc(GeneratedReport.generated_at)).all()

    return [
        ReportResponse(
            id=r.id,
            examination_id=r.examination_id,
            report_format=r.report_format,
            file_size_bytes=r.file_size_bytes,
            sha256_hash=r.sha256_hash,
            download_url=f"/api/reports/{r.id}/{r.report_format.lower()}",
            generated_at=r.generated_at,
        )
        for r in reports
    ]

@router.get("/reports/{report_id}/pdf")
def download_pdf_report(report_id: str, db: Session = Depends(get_db)):
    """Download official forensic PDF report."""
    rep = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not rep or rep.report_format.upper() != "PDF":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF report not found.")

    target = Path(rep.file_path)
    validated = validate_safe_path(target, settings.REPORTS_DIR)
    if not validated.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file missing from disk.")

    return FileResponse(
        path=str(validated),
        filename=f"SCSS_SATYA_Report_{report_id[:8].upper()}.pdf",
        media_type="application/pdf"
    )

@router.get("/reports/{report_id}/json")
def download_json_report(report_id: str, db: Session = Depends(get_db)):
    """Download official forensic JSON report."""
    rep = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not rep or rep.report_format.upper() != "JSON":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="JSON report not found.")

    target = Path(rep.file_path)
    validated = validate_safe_path(target, settings.REPORTS_DIR)
    if not validated.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file missing from disk.")

    with open(validated, "r", encoding="utf-8") as f:
        content = f.read()

    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=SCSS_SATYA_Report_{report_id[:8].upper()}.json"}
    )

@router.get("/reports/{report_id}/download")
def download_report_generic(report_id: str, db: Session = Depends(get_db)):
    """Generic download endpoint for generated forensic reports."""
    rep = db.query(GeneratedReport).filter(GeneratedReport.id == report_id).first()
    if not rep:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    
    if rep.report_format.upper() == "PDF":
        return download_pdf_report(report_id, db)
    return download_json_report(report_id, db)
