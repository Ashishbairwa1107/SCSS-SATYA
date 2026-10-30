import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database.session import get_db
from app.database.models import Case, Evidence, Examination
from app.schemas.case import CaseCreate, CaseResponse

router = APIRouter(prefix="/cases", tags=["Cases"])

def generate_case_reference() -> str:
    """Generate professional forensic case reference identifier: CAS-YYYYMMDD-XXXX."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    rand_suffix = uuid.uuid4().hex[:4].upper()
    return f"CAS-{date_str}-{rand_suffix}"

@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(case_in: CaseCreate, db: Session = Depends(get_db)):
    """Create a new forensic case container."""
    ref = case_in.case_reference or generate_case_reference()
    
    # Check duplicate reference
    existing = db.query(Case).filter(Case.case_reference == ref).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Case reference '{ref}' is already in use."
        )

    case = Case(
        case_reference=ref,
        title=case_in.title,
        purpose=case_in.purpose,
        evidence_source=case_in.evidence_source,
        investigator=case_in.investigator,
        notes=case_in.notes,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    return CaseResponse(
        id=case.id,
        case_reference=case.case_reference,
        title=case.title,
        purpose=case.purpose,
        evidence_source=case.evidence_source,
        investigator=case.investigator,
        notes=case.notes,
        created_at=case.created_at,
        updated_at=case.updated_at,
        evidence_count=0,
        examination_count=0,
    )

@router.get("", response_model=list[CaseResponse])
def list_cases(
    search: Optional[str] = Query(None, description="Search by title or reference"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve cases with search query and pagination."""
    query = db.query(Case)
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Case.title.ilike(search_filter)) | 
            (Case.case_reference.ilike(search_filter)) |
            (Case.investigator.ilike(search_filter))
        )

    cases = query.order_by(desc(Case.created_at)).offset(skip).limit(limit).all()

    results = []
    for c in cases:
        ev_count = db.query(func.count(Evidence.id)).filter(Evidence.case_id == c.id).scalar() or 0
        exam_count = db.query(func.count(Examination.id)).filter(Examination.case_id == c.id).scalar() or 0
        results.append(
            CaseResponse(
                id=c.id,
                case_reference=c.case_reference,
                title=c.title,
                purpose=c.purpose,
                evidence_source=c.evidence_source,
                investigator=c.investigator,
                notes=c.notes,
                created_at=c.created_at,
                updated_at=c.updated_at,
                evidence_count=ev_count,
                examination_count=exam_count,
            )
        )
    return results

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Retrieve detailed case record."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case record not found.")

    ev_count = db.query(func.count(Evidence.id)).filter(Evidence.case_id == case.id).scalar() or 0
    exam_count = db.query(func.count(Examination.id)).filter(Examination.case_id == case.id).scalar() or 0

    return CaseResponse(
        id=case.id,
        case_reference=case.case_reference,
        title=case.title,
        purpose=case.purpose,
        evidence_source=case.evidence_source,
        investigator=case.investigator,
        notes=case.notes,
        created_at=case.created_at,
        updated_at=case.updated_at,
        evidence_count=ev_count,
        examination_count=exam_count,
    )
