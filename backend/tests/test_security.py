import io
from app.core.security import validate_safe_path
from app.core.config import settings
from app.database.models import Evidence, Examination
from app.core.constants import ExaminationStatus
from fastapi import HTTPException
import pytest

def test_unsupported_file_extension_rejection(client):
    """Test 20: Rejection of non-image executable or script payloads."""
    files = {"file": ("malicious_payload.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")}
    res = client.post("/api/examinations", files=files)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]

def test_empty_file_rejection(client):
    """Test 21: Empty 0-byte file upload rejection."""
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    res = client.post("/api/examinations", files=files)
    assert res.status_code == 400
    assert "empty" in res.json()["detail"]

def test_corrupt_image_rejection(client):
    """Test 22: Corrupted or non-decodable file rejection."""
    files = {"file": ("corrupt.jpg", b"NOT_A_REAL_JPEG_HEADER_CORRUPTED", "image/jpeg")}
    res = client.post("/api/examinations", files=files)
    assert res.status_code == 400
    assert "decoding failed" in res.json()["detail"]

def test_path_traversal_prevention():
    """Test 23: Strict rejection of directory traversal attempts."""
    traversal_path = settings.VAULT_DIR / ".." / ".." / "Windows" / "System32" / "cmd.exe"
    with pytest.raises(HTTPException) as excinfo:
        validate_safe_path(traversal_path, settings.VAULT_DIR)
    assert excinfo.value.status_code == 403

def test_nonexistent_evidence_access(client):
    """Test 24: Secure 404 response on non-existent evidence or report queries."""
    res = client.get("/api/evidence/non-existent-uuid-12345")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_pipeline_resilience_on_failure(client, sample_jpeg_bytes, monkeypatch):
    """Test 25: Failure during downstream analysis stage preserves evidence record and records failure status."""
    import app.analysis.pipeline
    def broken_ela(*args, **kwargs):
        raise RuntimeError("Simulated transient analysis pipeline engine fault")

    monkeypatch.setattr(app.analysis.pipeline, "perform_error_level_analysis", broken_ela)

    files = {"file": ("fault_specimen.jpg", sample_jpeg_bytes, "image/jpeg")}
    res = client.post("/api/examinations", files=files)
    assert res.status_code == 201
    exam = res.json()
    assert exam["status"] == ExaminationStatus.FAILED.value
    assert "Simulated transient" in exam["failure_reason"]

    # Evidence record must remain preserved and verifiable!
    ev_id = exam["evidence_id"]
    ver_res = client.post(f"/api/evidence/{ev_id}/verify")
    assert ver_res.status_code == 200
    ver_data = ver_res.json()
    assert ver_data["status"] == "VERIFIED"
