import hashlib
from pathlib import Path
from app.core.config import settings
from app.core.constants import IntegrityStatus

def test_sha256_preservation_and_verification(client, sample_jpeg_bytes):
    """Test 9 & 10: Pristine SHA-256 calculation and verification endpoint."""
    expected_hash = hashlib.sha256(sample_jpeg_bytes).hexdigest().lower()

    files = {"file": ("unaltered_evidence.jpg", sample_jpeg_bytes, "image/jpeg")}
    res = client.post("/api/examinations", files=files)
    assert res.status_code == 201
    exam = res.json()
    evidence_id = exam["evidence_id"]

    # Verify returned hash matches independent hashlib computation
    assert exam["sha256_hash"].lower() == expected_hash

    # Call Layer 2 verification endpoint
    ver_res = client.post(f"/api/evidence/{evidence_id}/verify")
    assert ver_res.status_code == 200
    ver_data = ver_res.json()
    assert ver_data["status"] == IntegrityStatus.VERIFIED.value
    assert ver_data["recomputed_hash"].lower() == expected_hash
    assert "Stored evidence bytes match" in ver_data["message"]

def test_deliberate_tampering_detection(client, sample_jpeg_bytes):
    """Test 11: Deliberately modified stored evidence file produces integrity MISMATCH."""
    # Ingest evidence
    files = {"file": ("tamper_test.jpg", sample_jpeg_bytes, "image/jpeg")}
    res = client.post("/api/examinations", files=files)
    assert res.status_code == 201
    evidence_id = res.json()["evidence_id"]

    # Retrieve evidence detail via client
    ev_res = client.get(f"/api/evidence/{evidence_id}")
    assert ev_res.status_code == 200
    stored_filename = ev_res.json()["stored_filename"]
    vault_file_path = settings.VAULT_DIR / stored_filename
    assert vault_file_path.exists()

    # Read original stored bytes
    with open(vault_file_path, "rb") as f:
        stored_bytes = bytearray(f.read())

    # Deliberately modify 1 byte in the stored file (simulating bit rot or malicious unauthorized tampering)
    stored_bytes[10] = (stored_bytes[10] + 1) % 256
    with open(vault_file_path, "wb") as f:
        f.write(stored_bytes)

    # Call verification endpoint
    ver_res = client.post(f"/api/evidence/{evidence_id}/verify")
    assert ver_res.status_code == 200
    ver_data = ver_res.json()

    # Must detect mismatch!
    assert ver_data["status"] == IntegrityStatus.MISMATCH.value
    assert ver_data["recomputed_hash"].lower() != ver_data["expected_hash"].lower()
    assert "CRITICAL ALERT" in ver_data["message"]

    # Verify that dashboard metrics reflects integrity failure count
    metrics_res = client.get("/api/system/metrics")
    assert metrics_res.status_code == 200
    assert metrics_res.json()["integrity_failures"] >= 1
