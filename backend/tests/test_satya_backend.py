import io
import pytest
from app.core.constants import FindingStatus, ReviewStatus

def test_health_endpoint(client):
    """Test 1: Health endpoint returns healthy status and doctrine."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "The tool screens. The expert decides." in data["doctrine"]
    assert data["database_connected"] is True
    assert data["vault_accessible"] is True

def test_system_info_endpoint(client):
    """Test 2: System info endpoint exposes architecture and limits."""
    res = client.get("/api/system/info")
    assert res.status_code == 200
    data = res.json()
    assert data["platform_name"] == "SCSS SATYA"
    assert "JPEG" in data["supported_formats"]
    assert "PNG" in data["supported_formats"]

def test_case_creation_and_listing(client):
    """Test 3: Case creation persists case details with unique reference."""
    payload = {
        "title": "Suspected Forgery Inquest - Case #101",
        "case_reference": "CAS-TEST-0001",
        "purpose": "Verify document seal and stamp authenticity",
        "investigator": "Forensic Officer A. Sharma",
    }
    res = client.post("/api/cases", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["case_reference"] == "CAS-TEST-0001"
    assert data["title"] == payload["title"]

    # Test listing
    res_list = client.get("/api/cases?search=Sharma")
    assert res_list.status_code == 200
    cases = res_list.json()
    assert len(cases) >= 1
    assert any(c["case_reference"] == "CAS-TEST-0001" for c in cases)

def test_valid_image_ingestion_and_examination(client, sample_jpeg_bytes):
    """Test 4 & 5: Ingesting valid JPEG registers evidence and executes screening pipeline."""
    files = {
        "file": ("specimen_target.jpg", sample_jpeg_bytes, "image/jpeg")
    }
    data = {
        "case_title": "Primary Stamp Evidence",
        "purpose": "Digital authenticity screening",
        "investigator": "Dr. V. Menon",
    }
    res = client.post("/api/examinations", data=data, files=files)
    assert res.status_code == 201
    exam = res.json()
    assert exam["status"] == "COMPLETED"
    assert exam["original_filename"] == "specimen_target.jpg"
    assert exam["detected_format"] == "JPEG"
    assert len(exam["sha256_hash"]) == 64
    assert exam["findings_summary"]["total_findings"] >= 4

    exam_id = exam["id"]

    # Retrieve examination detail
    detail_res = client.get(f"/api/examinations/{exam_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["case"]["title"] == "Primary Stamp Evidence"
    assert len(detail["findings"]) >= 4

    # Validate each finding uses ONLY permitted 3 statuses
    valid_statuses = {FindingStatus.NO_INDICATOR.value, FindingStatus.INDICATOR_OBSERVED.value, FindingStatus.INCONCLUSIVE.value}
    for f in detail["findings"]:
        assert f["status"] in valid_statuses
        assert len(f["observed_evidence"]) > 0
        assert len(f["limitations"]) > 0
        assert len(f["recommended_action"]) > 0

def test_examiner_review_update(client, sample_jpeg_bytes):
    """Test 6: Examiner review persistence with qualifications and opinion."""
    # Ingest image first
    files = {"file": ("test_review.jpg", sample_jpeg_bytes, "image/jpeg")}
    res = client.post("/api/examinations", files=files)
    exam_id = res.json()["id"]

    # Update review with opinion
    review_payload = {
        "examiner_name": "Senior Examiner R. Kulkarni",
        "organization": "Sure Clue Scientific Solutions (SCSS)",
        "qualification": "Certified Digital Forensics Examiner (CDFE)",
        "qualitative_notes": "No gross visual incongruities observed along subject boundary.",
        "checklist_responses": [
            {"id": "chk_source_context", "label": "Source Context", "description": "Provenance check", "checked": True, "notes": "Verified"},
            {"id": "chk_ela_analysis", "label": "ELA Review", "description": "Residual check", "checked": True, "notes": "Nominal ELA"},
        ],
        "review_status": ReviewStatus.OPINION_RECORDED.value,
        "examiner_opinion": "Screening observations are consistent with single-generation capture. No positive indicators of tampering detected.",
        "confirm_opinion_disclosure": True,
    }

    put_res = client.put(f"/api/examinations/{exam_id}/review", json=review_payload)
    assert put_res.status_code == 200
    saved = put_res.json()
    assert saved["examiner_name"] == "Senior Examiner R. Kulkarni"
    assert saved["review_status"] == ReviewStatus.OPINION_RECORDED.value
    assert "single-generation capture" in saved["examiner_opinion"]
    assert len(saved["checklist_responses"]) == 2

def test_dashboard_metrics_consistency(client, sample_jpeg_bytes):
    """Test 7: Dashboard metrics accurately reflect real database counts."""
    res = client.get("/api/system/metrics")
    assert res.status_code == 200
    metrics = res.json()
    assert metrics["total_examinations"] >= 1
    assert metrics["total_cases"] >= 1
    assert metrics["total_evidence_items"] >= 1
    assert metrics["completed_examinations"] >= 1
    assert metrics["integrity_failures"] >= 0

def test_calibrated_specimen_generators(client):
    """Test 8: One-click calibrated test specimen endpoints."""
    # Specimen A: Camera-style
    res_a = client.post("/api/specimens/camera-style")
    assert res_a.status_code == 201
    exam_a = res_a.json()
    assert exam_a["status"] == "COMPLETED"
    assert exam_a["detected_format"] == "JPEG"

    # Specimen B: Spliced composite
    res_b = client.post("/api/specimens/spliced-composite")
    assert res_b.status_code == 201
    exam_b = res_b.json()
    assert exam_b["status"] == "COMPLETED"

    # Specimen C: Lossless PNG
    res_c = client.post("/api/specimens/lossless-png")
    assert res_c.status_code == 201
    exam_c = res_c.json()
    assert exam_c["detected_format"] == "PNG"
    assert exam_c["status"] == "COMPLETED"

def test_direct_evidence_registration_endpoint(client, sample_jpeg_bytes):
    """Test direct POST /api/evidence registration endpoint."""
    files = {"file": ("direct_evidence.jpg", sample_jpeg_bytes, "image/jpeg")}
    data = {"case_title": "Direct Evidence Registration Inquest"}
    res = client.post("/api/evidence", data=data, files=files)
    assert res.status_code == 201
    exam = res.json()
    assert exam["status"] == "COMPLETED"
    assert exam["original_filename"] == "direct_evidence.jpg"
    assert exam["evidence_id"] is not None
    assert len(exam["sha256_hash"]) == 64
