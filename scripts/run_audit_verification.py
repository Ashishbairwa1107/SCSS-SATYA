"""
SCSS SATYA — Complete Institutional Forensic Audit Script
Executes end-to-end verification of all four layers, cryptographic byte preservation,
tamper detection, report generation, lossless format rejection, and doctrine compliance.
"""
import sys
import os
from pathlib import Path
import hashlib
import json

# Setup path so app can be imported
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def run_audit():
    print("=" * 80)
    print("SCSS SATYA — FORENSIC IMAGE AUTHENTICITY SCREENING PLATFORM")
    print("COMPLETE END-TO-END IMPLEMENTATION & SCIENTIFIC AUDIT")
    print("Doctrine: 'The tool screens. The expert decides.'")
    print("=" * 80)

    audit_results = {}
    client = TestClient(app)

    # -------------------------------------------------------------------------
    # TEST 1: Health & System Configuration
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Verifying System Health & Configuration Endpoints...")
    health_res = client.get("/api/health")
    assert health_res.status_code == 200, f"Health check failed: {health_res.text}"
    health_data = health_res.json()
    assert health_data["status"] == "HEALTHY"
    assert health_data["database_connected"] is True
    assert health_data["vault_accessible"] is True
    print(f"  ✓ /api/health returned HEALTHY (database_connected={health_data['database_connected']}, vault_accessible={health_data['vault_accessible']})")

    sys_res = client.get("/api/system/info")
    assert sys_res.status_code == 200
    sys_data = sys_res.json()
    assert sys_data["doctrine"] == "The tool screens. The expert decides."
    assert sys_data["max_file_size_mb"] == 50
    print(f"  ✓ /api/system/info verified doctrine: \"{sys_data['doctrine']}\"")
    audit_results["TEST 1: Health & System Info"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 2: Case Container Creation
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Creating Forensic Case Container...")
    case_payload = {
        "title": "SEVA FIRST 2026 Audit Case - Forensic Benchmark",
        "purpose": "Comprehensive verification of 4-layer screening pipeline and evidence preservation",
        "evidence_source": "Laboratory Calibrated Synthetic Benchmarks",
        "investigator": "Lead Forensic Examiner (CFDE Certified)",
        "notes": "Automated institutional audit run"
    }
    case_res = client.post("/api/cases", json=case_payload)
    assert case_res.status_code == 201, f"Case creation failed: {case_res.text}"
    case_data = case_res.json()
    case_id = case_data["id"]
    case_ref = case_data["case_reference"]
    assert case_ref.startswith("CAS-")
    print(f"  ✓ Case created: ID={case_id}, Reference={case_ref}")
    audit_results["TEST 2: Case Creation"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 3: Evidence Ingestion & Cryptographic Byte Preservation (Specimen A)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Ingesting Specimen A (Camera Photo) & Verifying Cryptographic Preservation...")
    specimen_a_path = settings.BASE_DIR / "storage" / "specimens" / "specimen_a_camera_photo.jpg"
    assert specimen_a_path.exists(), f"Specimen A missing at {specimen_a_path}"

    with open(specimen_a_path, "rb") as f:
        specimen_a_raw = f.read()

    expected_sha256 = hashlib.sha256(specimen_a_raw).hexdigest()
    print(f"  Pre-ingestion SHA-256: {expected_sha256}")

    # Upload Specimen A
    upload_res = client.post(
        "/api/examinations",
        files={"file": ("specimen_a_camera_photo.jpg", specimen_a_raw, "image/jpeg")},
        data={"case_id": case_id, "investigator": "Lead Forensic Examiner"}
    )
    assert upload_res.status_code == 201, f"Ingestion failed: {upload_res.text}"
    exam_a = upload_res.json()
    exam_a_id = exam_a["id"]
    ev_a_id = exam_a["evidence_id"]

    # Ingestion hash must exactly match pre-ingestion byte hash
    assert exam_a["sha256_hash"] == expected_sha256, "Cryptographic hash mismatch at ingestion!"
    print(f"  ✓ Ingested SHA-256 matches exact byte hash: {exam_a['sha256_hash']}")

    # Get evidence details
    ev_res = client.get(f"/api/evidence/{ev_a_id}")
    assert ev_res.status_code == 200
    ev_a_data = ev_res.json()

    # Verify vault bytes are unaltered
    vault_file_path = settings.VAULT_DIR / ev_a_data["stored_filename"]
    assert vault_file_path.exists(), f"Vault file missing: {vault_file_path}"
    with open(vault_file_path, "rb") as f:
        stored_bytes = f.read()
    assert hashlib.sha256(stored_bytes).hexdigest() == expected_sha256, "Vault bytes altered on disk!"
    assert stored_bytes == specimen_a_raw, "Stored bytes differ from uploaded bytes!"
    print(f"  ✓ Vault byte preservation confirmed: {len(stored_bytes)} bytes untouched at {vault_file_path.name}")
    audit_results["TEST 3: Ingestion & Byte Preservation"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 4: Layer 1 Passive Screening Inspection (Specimen A)
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Inspecting Layer 1 Passive Screening Results (EXIF, ELA, Statistics)...")
    
    # 4A: Metadata
    meta_res = client.get(f"/api/evidence/{ev_a_id}/metadata")
    assert meta_res.status_code == 200, f"Metadata lookup failed: {meta_res.text}"
    meta_data = meta_res.json()
    assert meta_data["summary"]["has_exif"] is True
    print(f"  ✓ Metadata: Camera Make={meta_data['summary'].get('camera_make')}, Model={meta_data['summary'].get('camera_model')}")

    # 4B: JPEG ELA
    ela_res = client.get(f"/api/examinations/{exam_a_id}/ela")
    assert ela_res.status_code == 200
    ela_data = ela_res.json()
    assert ela_data["format_supported"] is True
    assert ela_data["quality"] == 90
    assert ela_data["scale"] == 15
    assert ela_data["artifact_url"] is not None
    assert ela_data["mean_difference"] is not None
    assert ela_data["max_difference"] is not None
    assert ela_data["residual_std"] is not None
    # Verify artifact file actually exists on disk and is reachable via API
    artifact_filename = ela_data["artifact_id"]
    art_res = client.get(f"/api/evidence/artifacts/{artifact_filename}")
    assert art_res.status_code == 200, f"ELA artifact fetch failed: {art_res.status_code}"
    assert len(art_res.content) > 0
    print(f"  ✓ JPEG ELA: Q={ela_data['quality']}, Scale={ela_data['scale']}x, MeanDiff={ela_data['mean_difference']}, Artifact={artifact_filename}")

    # 4C: RGB & Spatial Statistics
    stats_res = client.get(f"/api/examinations/{exam_a_id}/statistics")
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert "red" in stats_data["rgb_statistics"]
    assert len(stats_data["rgb_statistics"]["histogram"]) == 32
    assert "laplacian_variance" in stats_data["spatial_noise"]
    print(f"  ✓ RGB Statistics: 32-bin histograms, Laplacian focus variance={stats_data['spatial_noise']['laplacian_variance']:.2f}")
    audit_results["TEST 4: Layer 1 Passive Screening"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 5: Layer 3 Explainable Technical Findings
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Validating Layer 3 Explainable Findings & No Arbitrary Percentages...")
    detail_res = client.get(f"/api/examinations/{exam_a_id}")
    assert detail_res.status_code == 200
    exam_detail = detail_res.json()
    findings = exam_detail["findings"]
    assert len(findings) == 5, f"Expected 5 forensic indicator findings, got {len(findings)}"

    for f in findings:
        assert f["status"] in ["No Indicator Detected", "Indicator Observed", "Inconclusive"]
        # Confirm NO arbitrary percentage claims
        for field in ["observed_evidence", "explanation", "significance", "limitations"]:
            val = f.get(field, "")
            assert "% fake" not in val.lower()
            assert "% genuine" not in val.lower()
            assert "% manipulated" not in val.lower()
        print(f"  ✓ Finding '{f['indicator_name']}': [{f['status']}] - {f['observed_evidence'][:60]}...")
    audit_results["TEST 5: Layer 3 Explainable Findings"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 6: Layer 2 Integrity Verification & Deliberate Tampering Detection
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Testing Layer 2 Cryptographic Re-Verification & Deliberate Bit Tampering Detection...")
    # Step 6A: Clean verification
    ver_res = client.post(f"/api/evidence/{ev_a_id}/verify")
    assert ver_res.status_code == 200
    ver_data = ver_res.json()
    assert ver_data["status"] == "VERIFIED"
    assert ver_data["expected_hash"] == ver_data["recomputed_hash"]
    print(f"  ✓ Clean verification: Status={ver_data['status']}, Hash={ver_data['recomputed_hash'][:16]}...")

    # Step 6B: Deliberate 1-byte file alteration test on a separate evidence container
    temp_bytes = bytearray(specimen_a_raw)
    temp_upload = client.post(
        "/api/examinations",
        files={"file": ("tamper_test.jpg", bytes(temp_bytes), "image/jpeg")},
        data={"case_id": case_id, "investigator": "Integrity Test Rig"}
    )
    assert temp_upload.status_code == 201
    temp_ev_id = temp_upload.json()["evidence_id"]
    temp_ev_data = client.get(f"/api/evidence/{temp_ev_id}").json()
    temp_vault_filename = temp_ev_data["stored_filename"]
    temp_vault_path = settings.VAULT_DIR / temp_vault_filename

    # Deliberately modify byte at offset 100
    with open(temp_vault_path, "r+b") as tf:
        tf.seek(100)
        orig_byte = tf.read(1)
        tf.seek(100)
        tf.write(bytes([orig_byte[0] ^ 0xFF]))

    # Now run Layer 2 verification against altered file
    tamper_ver = client.post(f"/api/evidence/{temp_ev_id}/verify")
    assert tamper_ver.status_code == 200
    tamper_data = tamper_ver.json()
    assert tamper_data["status"] == "MISMATCH", f"Tampering was NOT detected! Status: {tamper_data['status']}"
    assert tamper_data["expected_hash"] != tamper_data["recomputed_hash"]
    print(f"  ✓ Deliberate Bit Tampering: Successfully detected hash mismatch! Status={tamper_data['status']}")
    print(f"    Expected:   {tamper_data['expected_hash']}")
    print(f"    Recomputed: {tamper_data['recomputed_hash']}")
    audit_results["TEST 6: Layer 2 Verification & Tamper Detection"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 7: Layer 4 Human Forensic Review
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Saving Qualified Human Forensic Review & Opinion...")
    review_payload = {
        "examiner_name": "Dr. K. Swaminathan",
        "organization": "Sure Clue Scientific Solutions (SCSS)",
        "qualification": "Certified Forensic Document Examiner (CFDE, IAI)",
        "qualitative_notes": "Single-generation capture characteristics with coherent luminance, focus gradient, and uncompressed EXIF tags.",
        "review_status": "Examiner Opinion Recorded",
        "examiner_opinion": "Technical screening observations are consistent with single-generation digital capture. No structural composite or quantization anomalies observed.",
        "checklist_responses": [
            {"id": "chk_source_context", "label": "Original Source & Acquisition Context", "description": "Checked", "checked": True, "notes": "Specimen verified against camera benchmark"},
            {"id": "chk_chain_of_custody", "label": "Chain of Custody & Hash Preservation", "description": "Checked", "checked": True, "notes": "SHA-256 confirmed intact"}
        ],
        "confirm_opinion_disclosure": True
    }
    rev_res = client.put(f"/api/examinations/{exam_a_id}/review", json=review_payload)
    assert rev_res.status_code == 200, f"Review update failed: {rev_res.text}"
    rev_data = rev_res.json()
    assert rev_data["review_status"] == "Examiner Opinion Recorded"
    assert rev_data["credential_status"] in ["UNVERIFIED", "QUALIFIED"]
    print(f"  ✓ Human Review recorded: Status={rev_data['review_status']}, Examiner={rev_data['examiner_name']}, Credential={rev_data['credential_status']}")
    audit_results["TEST 7: Layer 4 Human Review"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 8: Report Generation (PDF & JSON)
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Generating and Downloading PDF & JSON Forensic Reports...")
    # 8A: PDF Report
    pdf_gen_res = client.post(f"/api/examinations/{exam_a_id}/reports", json={"report_format": "PDF"})
    assert pdf_gen_res.status_code == 201, f"PDF report generation failed: {pdf_gen_res.text}"
    pdf_info = pdf_gen_res.json()
    pdf_id = pdf_info["id"]

    pdf_dl_res = client.get(pdf_info["download_url"])
    assert pdf_dl_res.status_code == 200
    assert pdf_dl_res.content.startswith(b"%PDF-"), "Downloaded PDF is missing %PDF- magic bytes!"
    print(f"  ✓ PDF Report generated: {len(pdf_dl_res.content):,} bytes, SHA-256={pdf_info['sha256_hash'][:16]}..., Header=%PDF-")

    # 8B: JSON Report
    json_gen_res = client.post(f"/api/examinations/{exam_a_id}/reports", json={"report_format": "JSON"})
    assert json_gen_res.status_code == 201
    json_info = json_gen_res.json()
    json_id = json_info["id"]

    json_dl_res = client.get(json_info["download_url"])
    assert json_dl_res.status_code == 200
    json_doc = json.loads(json_dl_res.content.decode("utf-8"))
    assert json_doc["$schema_version"] == "1.0.0"
    assert json_doc["platform"]["doctrine"] == "The tool screens. The expert decides."
    assert "forensic_layer_results" in json_doc
    assert "evidence" in json_doc
    assert "layer_3_explainable_findings" in json_doc["forensic_layer_results"]
    assert "layer_4_human_review" in json_doc["forensic_layer_results"]
    print(f"  ✓ JSON Report generated: Schema v{json_doc['$schema_version']}, Valid JSON, SHA-256={json_info['sha256_hash'][:16]}...")
    audit_results["TEST 8: Report Generation"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 9: Lossless Format Rejection for JPEG ELA (Specimen C - PNG)
    # -------------------------------------------------------------------------
    print("\n[TEST 9] Ingesting Specimen C (Lossless PNG) & Verifying ELA Refusal...")
    specimen_c_path = settings.BASE_DIR / "storage" / "specimens" / "specimen_c_lossless_chart.png"
    assert specimen_c_path.exists(), f"Specimen C missing at {specimen_c_path}"
    with open(specimen_c_path, "rb") as f:
        specimen_c_raw = f.read()

    png_upload = client.post(
        "/api/examinations",
        files={"file": ("specimen_c_lossless_chart.png", specimen_c_raw, "image/png")},
        data={"case_id": case_id, "investigator": "Lossless Format Tester"}
    )
    assert png_upload.status_code == 201
    exam_c_id = png_upload.json()["id"]

    png_ela_res = client.get(f"/api/examinations/{exam_c_id}/ela")
    assert png_ela_res.status_code == 200
    png_ela = png_ela_res.json()
    assert png_ela["format_supported"] is False, "Lossless PNG was falsely processed with JPEG ELA!"
    assert "not applicable to lossless" in png_ela["notes"].lower()
    print(f"  ✓ Lossless PNG ELA refusal: format_supported={png_ela['format_supported']}, Reason: \"{png_ela['notes'][:80]}...\"")

    # Check finding for ELA residuals on PNG
    png_detail = client.get(f"/api/examinations/{exam_c_id}").json()
    ela_finding = next((f for f in png_detail["findings"] if f["finding_key"] == "FINDING_ELA_RESIDUALS"), None)
    assert ela_finding is not None
    assert ela_finding["status"] == "Inconclusive", f"Expected Inconclusive for PNG ELA finding, got {ela_finding['status']}"
    print(f"  ✓ PNG ELA finding correctly marked '{ela_finding['status']}'")
    audit_results["TEST 9: Lossless PNG ELA Refusal"] = "PASSED"

    # -------------------------------------------------------------------------
    # TEST 10: Dashboard Metrics Integrity
    # -------------------------------------------------------------------------
    print("\n[TEST 10] Checking Dashboard Metrics...")
    metrics_res = client.get("/api/dashboard/metrics")
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    assert metrics["total_cases"] >= 1
    assert metrics["total_examinations"] >= 3
    assert metrics["integrity_failures"] >= 1  # Should include our intentional tampering test!
    print(f"  ✓ Dashboard metrics verified: Cases={metrics['total_cases']}, Exams={metrics['total_examinations']}, Integrity Failures={metrics['integrity_failures']}")
    audit_results["TEST 10: Dashboard Metrics"] = "PASSED"

    # -------------------------------------------------------------------------
    # Final Summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("AUDIT SUMMARY RESULTS:")
    print("=" * 80)
    all_passed = True
    for test_name, status in audit_results.items():
        print(f"  {test_name.ljust(50)}: {status}")
        if status != "PASSED":
            all_passed = False

    print("=" * 80)
    if all_passed:
        print("ALL 10 FORENSIC AUDIT BENCHMARKS PASSED SUCCESSFULLY!")
    else:
        print("SOME BENCHMARKS FAILED.")
    print("=" * 80)

if __name__ == "__main__":
    run_audit()
