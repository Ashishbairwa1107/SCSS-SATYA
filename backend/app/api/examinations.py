import io
import json
from pathlib import Path
from typing import Optional
from PIL import Image
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database.session import get_db
from app.database.models import Case, Evidence, Examination, AnalysisResult, Finding, ExaminerReview, IntegrityVerification
from app.schemas.examination import ExaminationResponse, ExaminationDetailResponse, FindingsSummary
from app.schemas.case import CaseResponse
from app.schemas.evidence import EvidenceResponse
from app.schemas.analysis import FindingResponse
from app.schemas.review import ExaminerReviewResponse
from app.services.storage import storage_service
from app.services.audit import log_audit_event
from app.analysis.pipeline import run_screening_pipeline
from app.core.config import settings
from app.core.constants import FindingStatus, ExaminationStatus, AuditEventType, IntegrityStatus
from app.api.cases import generate_case_reference

router = APIRouter(prefix="/examinations", tags=["Examinations"])

@router.post("", response_model=ExaminationResponse, status_code=status.HTTP_201_CREATED)
def create_examination(
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
    Ingest evidence image, compute SHA-256 cryptographic digest directly from uploaded bytes,
    preserve pristine original in vault, and initiate the 4-Layer Forensic Screening Pipeline.
    """
    # 1. Read original bytes
    contents = file.file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if len(contents) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
        )

    # 2. Check extension and decode with PIL safely (decompression bomb protection)
    original_filename = file.filename or "evidence_file.bin"
    ext = Path(original_filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Allowed extensions: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}"
        )

    # Set decompression limit
    Image.MAX_IMAGE_PIXELS = settings.MAX_IMAGE_PIXELS
    try:
        with Image.open(io.BytesIO(contents)) as test_img:
            test_img.verify()  # verify integrity of container
        with Image.open(io.BytesIO(contents)) as test_img:
            detected_format = test_img.format or "UNKNOWN"
            width, height = test_img.size
            color_mode = test_img.mode
            
            # Dimension checks
            if width > settings.MAX_IMAGE_DIMENSION or height > settings.MAX_IMAGE_DIMENSION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image dimensions ({width}x{height}) exceed maximum allowed dimension of {settings.MAX_IMAGE_DIMENSION}px."
                )
            if (width * height) > settings.MAX_IMAGE_PIXELS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image pixel count exceeds safe decompression limit."
                )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image decoding failed or corrupted file container: {str(exc)}"
        )

    # 3. Store unaltered evidence bytes into protected vault & compute SHA-256
    stored_filename, storage_path, file_size, sha256_hash = storage_service.save_evidence_bytes(
        data=contents,
        original_filename=original_filename,
    )

    # 4. Resolve or create Case
    case = None
    if case_id:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Target case {case_id} not found.")
    elif case_reference and case_reference.strip():
        clean_ref = case_reference.strip()
        existing_case = db.query(Case).filter(Case.case_reference == clean_ref).first()
        if existing_case:
            case = existing_case
        else:
            title = case_title or f"Forensic Case: {original_filename}"
            case = Case(
                case_reference=clean_ref,
                title=title,
                purpose=purpose or "Image authenticity screening and evidence preservation",
                evidence_source=evidence_source or "Field digital acquisition",
                investigator=investigator or "Authorized Forensic Examiner",
                notes=notes,
            )
            db.add(case)
            db.commit()
            db.refresh(case)
    else:
        ref = generate_case_reference()
        while db.query(Case).filter(Case.case_reference == ref).first():
            ref = generate_case_reference()
        title = case_title or f"Forensic Case: {original_filename}"
        case = Case(
            case_reference=ref,
            title=title,
            purpose=purpose or "Image authenticity screening and evidence preservation",
            evidence_source=evidence_source or "Field digital acquisition",
            investigator=investigator or "Authorized Forensic Examiner",
            notes=notes,
        )
        db.add(case)
        db.commit()
        db.refresh(case)

    # 5. Create Evidence record
    evidence = Evidence(
        case_id=case.id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_size_bytes=file_size,
        mime_type=file.content_type or f"image/{detected_format.lower()}",
        detected_format=detected_format,
        width=width,
        height=height,
        color_mode=color_mode,
        sha256_hash=sha256_hash,
        storage_path=storage_path,
        is_specimen=False,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    # Record initial integrity verification
    init_ver = IntegrityVerification(
        evidence_id=evidence.id,
        expected_hash=sha256_hash,
        recomputed_hash=sha256_hash,
        status=IntegrityStatus.VERIFIED.value,
        details="Initial ingestion SHA-256 digest calculated and recorded.",
    )
    db.add(init_ver)

    # Log ingestion audit event
    log_audit_event(
        db,
        event_type=AuditEventType.EVIDENCE_INGESTED,
        entity_type="Evidence",
        entity_id=evidence.id,
        case_id=case.id,
        details={
            "filename": original_filename,
            "sha256": sha256_hash,
            "format": detected_format,
            "bytes": file_size,
        }
    )

    # 6. Create Examination
    examination = Examination(
        case_id=case.id,
        evidence_id=evidence.id,
        status=ExaminationStatus.PENDING.value,
    )
    db.add(examination)
    db.commit()
    db.refresh(examination)

    # 7. Execute screening pipeline
    run_screening_pipeline(db, examination.id)
    db.refresh(examination)

    # Prepare response summary
    findings = db.query(Finding).filter(Finding.examination_id == examination.id).all()
    no_ind = sum(1 for f in findings if f.status == FindingStatus.NO_INDICATOR.value)
    ind_obs = sum(1 for f in findings if f.status == FindingStatus.INDICATOR_OBSERVED.value)
    inconcl = sum(1 for f in findings if f.status == FindingStatus.INCONCLUSIVE.value)

    review = db.query(ExaminerReview).filter(ExaminerReview.examination_id == examination.id).first()

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
        review_status=review.review_status if review else "Pending Review",
        integrity_status=IntegrityStatus.VERIFIED.value,
        findings_summary=FindingsSummary(
            no_indicator_count=no_ind,
            indicator_observed_count=ind_obs,
            inconclusive_count=inconcl,
            total_findings=len(findings),
        )
    )

@router.get("", response_model=list[ExaminationResponse])
def list_examinations(
    search: Optional[str] = Query(None, description="Search by case reference or filename"),
    format_filter: Optional[str] = Query(None, description="Filter by format (e.g. JPEG, PNG)"),
    review_status: Optional[str] = Query(None, description="Filter by examiner review status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve list of examinations with search, format, and status filters."""
    query = db.query(Examination).join(Evidence, Examination.evidence_id == Evidence.id).join(Case, Examination.case_id == Case.id)

    if search:
        s_filter = f"%{search}%"
        query = query.filter(
            (Case.case_reference.ilike(s_filter)) |
            (Case.title.ilike(s_filter)) |
            (Evidence.original_filename.ilike(s_filter)) |
            (Evidence.sha256_hash.ilike(s_filter))
        )

    if format_filter:
        query = query.filter(Evidence.detected_format.ilike(format_filter))

    exams = query.order_by(desc(Examination.started_at)).offset(skip).limit(limit).all()

    results = []
    for ex in exams:
        case = ex.case
        evidence = ex.evidence
        review = ex.review

        findings = ex.findings
        no_ind = sum(1 for f in findings if f.status == FindingStatus.NO_INDICATOR.value)
        ind_obs = sum(1 for f in findings if f.status == FindingStatus.INDICATOR_OBSERVED.value)
        inconcl = sum(1 for f in findings if f.status == FindingStatus.INCONCLUSIVE.value)

        latest_ver = db.query(IntegrityVerification).filter(
            IntegrityVerification.evidence_id == evidence.id
        ).order_by(desc(IntegrityVerification.verified_at)).first()

        int_status = latest_ver.status if latest_ver else IntegrityStatus.UNVERIFIED.value

        if review_status and review and review.review_status != review_status:
            continue

        results.append(
            ExaminationResponse(
                id=ex.id,
                case_id=case.id,
                evidence_id=evidence.id,
                status=ex.status,
                failure_reason=ex.failure_reason,
                started_at=ex.started_at,
                completed_at=ex.completed_at,
                case_reference=case.case_reference,
                case_title=case.title,
                original_filename=evidence.original_filename,
                detected_format=evidence.detected_format,
                sha256_hash=evidence.sha256_hash,
                review_status=review.review_status if review else "Pending Review",
                integrity_status=int_status,
                findings_summary=FindingsSummary(
                    no_indicator_count=no_ind,
                    indicator_observed_count=ind_obs,
                    inconclusive_count=inconcl,
                    total_findings=len(findings),
                )
            )
        )
    return results

@router.get("/{examination_id}", response_model=ExaminationDetailResponse)
def get_examination_detail(examination_id: str, db: Session = Depends(get_db)):
    """Retrieve full examination dossier including case, evidence, findings, review, and exhibits."""
    ex = db.query(Examination).filter(Examination.id == examination_id).first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examination record not found.")

    case = ex.case
    evidence = ex.evidence
    findings = ex.findings
    review = ex.review
    analysis = ex.analysis_result

    no_ind = sum(1 for f in findings if f.status == FindingStatus.NO_INDICATOR.value)
    ind_obs = sum(1 for f in findings if f.status == FindingStatus.INDICATOR_OBSERVED.value)
    inconcl = sum(1 for f in findings if f.status == FindingStatus.INCONCLUSIVE.value)

    # Checklist parsing
    checklist_resp = []
    if review and review.checklist_responses_json:
        try:
            checklist_resp = json.loads(review.checklist_responses_json)
        except Exception:
            checklist_resp = []

    review_out = None
    if review:
        review_out = ExaminerReviewResponse(
            id=review.id,
            examination_id=review.examination_id,
            examiner_name=review.examiner_name,
            organization=review.organization,
            qualification=review.qualification,
            credential_status=review.credential_status,
            qualitative_notes=review.qualitative_notes,
            checklist_responses=checklist_resp,
            review_status=review.review_status,
            examiner_opinion=review.examiner_opinion,
            reviewed_at=review.reviewed_at,
            updated_at=review.updated_at,
        )

    # Integrity status
    latest_ver = db.query(IntegrityVerification).filter(
        IntegrityVerification.evidence_id == evidence.id
    ).order_by(desc(IntegrityVerification.verified_at)).first()
    int_status = latest_ver.status if latest_ver else IntegrityStatus.UNVERIFIED.value

    return ExaminationDetailResponse(
        id=ex.id,
        case_id=case.id,
        evidence_id=evidence.id,
        status=ex.status,
        failure_reason=ex.failure_reason,
        started_at=ex.started_at,
        completed_at=ex.completed_at,
        case=CaseResponse(
            id=case.id,
            case_reference=case.case_reference,
            title=case.title,
            purpose=case.purpose,
            evidence_source=case.evidence_source,
            investigator=case.investigator,
            notes=case.notes,
            created_at=case.created_at,
            updated_at=case.updated_at,
        ),
        evidence=EvidenceResponse(
            id=evidence.id,
            case_id=evidence.case_id,
            original_filename=evidence.original_filename,
            stored_filename=evidence.stored_filename,
            file_size_bytes=evidence.file_size_bytes,
            mime_type=evidence.mime_type,
            detected_format=evidence.detected_format,
            width=evidence.width,
            height=evidence.height,
            color_mode=evidence.color_mode,
            sha256_hash=evidence.sha256_hash,
            ingestion_timestamp=evidence.ingestion_timestamp,
            is_specimen=evidence.is_specimen,
            specimen_type=evidence.specimen_type,
            integrity_status=int_status,
        ),
        findings=[
            FindingResponse(
                id=f.id,
                finding_key=f.finding_key,
                indicator_name=f.indicator_name,
                status=f.status,
                observed_evidence=f.observed_evidence,
                explanation=f.explanation,
                significance=f.significance,
                limitations=f.limitations,
                recommended_action=f.recommended_action,
                order_index=f.order_index,
            ) for f in sorted(findings, key=lambda x: x.order_index)
        ],
        review=review_out,
        findings_summary=FindingsSummary(
            no_indicator_count=no_ind,
            indicator_observed_count=ind_obs,
            inconclusive_count=inconcl,
            total_findings=len(findings),
        ),
        has_ela=bool(analysis and analysis.ela_format_supported and analysis.ela_artifact_path),
        has_statistics=bool(analysis and analysis.rgb_statistics_json),
    )

@router.get("/{examination_id}/findings", response_model=list[FindingResponse])
def get_examination_findings(examination_id: str, db: Session = Depends(get_db)):
    """Retrieve explainable technical findings for specified examination."""
    findings = db.query(Finding).filter(
        Finding.examination_id == examination_id
    ).order_by(Finding.order_index).all()
    return findings
