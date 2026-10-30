import json
import hashlib

def test_report_generation_pdf_and_json(client, sample_jpeg_bytes):
    """Test 17, 18 & 19: PDF and JSON official forensic report generation."""
    # Ingest evidence
    files = {"file": ("report_specimen.jpg", sample_jpeg_bytes, "image/jpeg")}
    exam_res = client.post("/api/examinations", files=files)
    exam_id = exam_res.json()["id"]

    # 1. Generate PDF Report
    pdf_res = client.post(f"/api/examinations/{exam_id}/reports", json={"report_format": "PDF"})
    assert pdf_res.status_code == 201
    pdf_meta = pdf_res.json()
    assert pdf_meta["report_format"] == "PDF"
    assert len(pdf_meta["sha256_hash"]) == 64
    pdf_report_id = pdf_meta["id"]

    # Download PDF
    dl_pdf = client.get(f"/api/reports/{pdf_report_id}/pdf")
    assert dl_pdf.status_code == 200
    assert dl_pdf.content.startswith(b"%PDF-")
    # Verify hash of downloaded PDF matches recorded report hash
    computed_pdf_hash = hashlib.sha256(dl_pdf.content).hexdigest().lower()
    assert computed_pdf_hash == pdf_meta["sha256_hash"].lower()

    # 2. Generate JSON Report
    json_res = client.post(f"/api/examinations/{exam_id}/reports", json={"report_format": "JSON"})
    assert json_res.status_code == 201
    json_meta = json_res.json()
    assert json_meta["report_format"] == "JSON"
    json_report_id = json_meta["id"]

    # Download JSON
    dl_json = client.get(f"/api/reports/{json_report_id}/json")
    assert dl_json.status_code == 200
    report_json_data = json.loads(dl_json.text)
    assert report_json_data["$schema_version"] == "1.0.0"
    assert "platform" in report_json_data
    assert "forensic_layer_results" in report_json_data
    assert "legal_and_scientific_disclaimer" in report_json_data
    assert "The tool screens. The expert decides." in report_json_data["platform"]["doctrine"]
