import hashlib
import uuid
from pathlib import Path
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import validate_safe_path, sanitize_filename

class StorageService:
    @staticmethod
    def calculate_sha256(data: bytes) -> str:
        """Compute cryptographic SHA-256 hash strictly from byte payload."""
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest().lower()

    @staticmethod
    def save_evidence_bytes(data: bytes, original_filename: str) -> tuple[str, str, int, str]:
        """
        Store pristine evidence bytes into protected vault.
        Returns: (stored_filename, storage_path_str, file_size_bytes, sha256_hash)
        """
        if len(data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Evidence file payload is empty (0 bytes)."
            )

        if len(data) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Evidence file exceeds maximum permitted size of {settings.MAX_FILE_SIZE_BYTES // (1024*1024)} MB."
            )

        # Calculate SHA-256 strictly from original raw evidence bytes
        sha256_hash = StorageService.calculate_sha256(data)

        # Determine safe extension
        sanitized = sanitize_filename(original_filename)
        ext = Path(sanitized).suffix.lower()
        if not ext:
            ext = ".bin"

        # Unique randomized non-overwriting storage filename
        stored_filename = f"evd_{uuid.uuid4().hex}_{sha256_hash[:8]}{ext}"
        target_path = settings.VAULT_DIR / stored_filename

        # Ensure safe path
        validated_path = validate_safe_path(target_path, settings.VAULT_DIR)

        # Write pristine evidence bytes
        with open(validated_path, "wb") as f:
            f.write(data)

        return stored_filename, str(validated_path), len(data), sha256_hash

    @staticmethod
    def verify_evidence_integrity(storage_path_str: str, expected_hash: str) -> tuple[bool, str]:
        """
        Re-read stored bytes directly from vault and verify matching SHA-256 hash.
        Returns: (is_valid, recomputed_hash)
        """
        target_path = Path(storage_path_str)
        validated_path = validate_safe_path(target_path, settings.VAULT_DIR)

        if not validated_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence file could not be located in storage vault."
            )

        with open(validated_path, "rb") as f:
            stored_bytes = f.read()

        recomputed_hash = StorageService.calculate_sha256(stored_bytes)
        is_match = (recomputed_hash.lower() == expected_hash.lower())
        return is_match, recomputed_hash

    @staticmethod
    def save_artifact(data: bytes, extension: str, prefix: str = "art") -> tuple[str, str]:
        """
        Save derived analysis exhibit (e.g. ELA heatmap or preview) into artifacts directory.
        Returns: (artifact_filename, artifact_path_str)
        """
        artifact_filename = f"{prefix}_{uuid.uuid4().hex}{extension}"
        target_path = settings.ARTIFACTS_DIR / artifact_filename
        validated_path = validate_safe_path(target_path, settings.ARTIFACTS_DIR)

        with open(validated_path, "wb") as f:
            f.write(data)

        return artifact_filename, str(validated_path)

    @staticmethod
    def save_report(data: bytes, extension: str, prefix: str = "report") -> tuple[str, str, int, str]:
        """
        Save generated PDF or JSON forensic report.
        Returns: (report_filename, report_path_str, file_size_bytes, sha256_hash)
        """
        sha256_hash = StorageService.calculate_sha256(data)
        report_filename = f"{prefix}_{uuid.uuid4().hex[:12]}_{sha256_hash[:8]}{extension}"
        target_path = settings.REPORTS_DIR / report_filename
        validated_path = validate_safe_path(target_path, settings.REPORTS_DIR)

        with open(validated_path, "wb") as f:
            f.write(data)

        return report_filename, str(validated_path), len(data), sha256_hash

storage_service = StorageService()
