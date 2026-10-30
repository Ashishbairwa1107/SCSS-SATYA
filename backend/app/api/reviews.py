import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Examination, ExaminerReview
from app.schemas.review import ExaminerReviewResponse, ExaminerReviewUpdate, ChecklistItem
from app.services.audit import log_audit_event
from app.core.constants import ReviewStatus, AuditEventType

router = APIRouter(prefix="/examinations", tags=["Examiner Review"])

@router.get("/{examination_id}/review", response_model=ExaminerReviewResponse)
def get_examiner_review(examination_id: str, db: Session = Depends(get_db)):
    """Retrieve human examiner review dossier, checklist responses, and recorded opinions."""
    ex = db.query(Examination).filter(Examination.id == examination_id).first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examination not found.")

    review = ex.review
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examiner review record not initialized.")

    checklist_resp = []
    if review.checklist_responses_json:
        try:
            checklist_resp = json.loads(review.checklist_responses_json)
        except Exception:
            checklist_resp = []

    return ExaminerReviewResponse(
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

@router.put("/{examination_id}/review", response_model=ExaminerReviewResponse)
def update_examiner_review(
    examination_id: str,
    update_data: ExaminerReviewUpdate,
    db: Session = Depends(get_db)
):
    """
    Save or update qualified human forensic review.
    If recording a formal examiner opinion, requires explicit confirmation disclosure.
    Audit trail event is logged.
    """
    ex = db.query(Examination).filter(Examination.id == examination_id).first()
    if not ex:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examination not found.")

    review = ex.review
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examiner review record not found.")

    # Validate opinion disclosure requirement
    if update_data.review_status == ReviewStatus.OPINION_RECORDED.value:
        if not update_data.examiner_opinion or not update_data.examiner_opinion.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Examiner opinion text must be provided when status is 'Examiner Opinion Recorded'."
            )
        if not update_data.confirm_opinion_disclosure:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Confirmation disclosure must be accepted: opinion is entered by qualified human examiner and not software-generated."
            )

    review.examiner_name = update_data.examiner_name
    review.organization = update_data.organization
    review.qualification = update_data.qualification
    review.qualitative_notes = update_data.qualitative_notes
    review.review_status = update_data.review_status
    review.examiner_opinion = update_data.examiner_opinion
    review.checklist_responses_json = json.dumps([item.model_dump() for item in update_data.checklist_responses])
    review.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(review)

    log_audit_event(
        db,
        event_type=AuditEventType.EXAMINER_REVIEW_SAVED,
        entity_type="ExaminerReview",
        entity_id=review.id,
        case_id=ex.case_id,
        details={
            "examiner": review.examiner_name,
            "status": review.review_status,
            "checklist_items_count": len(update_data.checklist_responses),
        }
    )

    checklist_resp = []
    if review.checklist_responses_json:
        try:
            checklist_resp = json.loads(review.checklist_responses_json)
        except Exception:
            checklist_resp = []

    return ExaminerReviewResponse(
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
