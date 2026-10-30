import json
from typing import Optional, Any
from sqlalchemy.orm import Session
from app.database.models import AuditEvent
from app.core.constants import AuditEventType

def log_audit_event(
    db: Session,
    event_type: AuditEventType,
    entity_type: str,
    entity_id: str,
    case_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
) -> AuditEvent:
    """Record an audit trail event in the database."""
    details_str = json.dumps(details) if details else None
    event = AuditEvent(
        event_type=event_type.value if hasattr(event_type, "value") else str(event_type),
        entity_type=entity_type,
        entity_id=entity_id,
        case_id=case_id,
        details_json=details_str,
    )
    db.add(event)
    try:
        db.commit()
        db.refresh(event)
    except Exception:
        db.rollback()
        raise
    return event
