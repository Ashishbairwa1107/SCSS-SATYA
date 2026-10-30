import re
import os
from pathlib import Path
from fastapi import HTTPException, status
from app.core.config import settings

def sanitize_filename(filename: str) -> str:
    """Sanitize user-provided filename to prevent path traversal or special characters."""
    base = os.path.basename(filename)
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', base)
    if not clean or clean.startswith('.'):
        clean = f"evidence_{clean}"
    return clean[:100]

def validate_safe_path(target_path: Path, allowed_root: Path) -> Path:
    """Ensure target_path resolves strictly within allowed_root to eliminate directory traversal."""
    try:
        resolved_target = target_path.resolve()
        resolved_root = allowed_root.resolve()
        # Verify target is relative to root
        resolved_target.relative_to(resolved_root)
        return resolved_target
    except (ValueError, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Path traversal detected or path outside storage root."
        )

def sanitize_exception(exc: Exception) -> str:
    """Format exceptions without exposing absolute system filesystem paths or sensitive credentials."""
    msg = str(exc)
    for sensitive_path in [str(settings.PROJECT_ROOT), str(settings.STORAGE_DIR)]:
        msg = msg.replace(sensitive_path, "[STORAGE_ROOT]")
    return msg
