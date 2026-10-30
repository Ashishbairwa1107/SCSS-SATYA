import sys
import hashlib
from pathlib import Path
from PIL import Image
import io

backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

def test_full_workflow():
    print("======================================================================")
    print("Testing Complete Workflow: Upload -> Register -> SHA-256 -> Screening")
    print("======================================================================")

    client = TestClient(app)

    # 1. Prepare genuine test JPEG with visual regions
    print("\n[Step 1] Creating test JPEG evidence image...")
    jpeg_img = Image.new("RGB", (320, 240), color=(180, 40, 40))
    for x in range(60, 260):
        for y in range(40, 180):
            jpeg_img.putpixel((x, y), (40, 140, 220))
    jpeg_buf = io.BytesIO()
    jpeg_img.save(jpeg_buf, format="JPEG", quality=95)
    jpeg_bytes = jpeg_buf.getvalue()
    expected_jpeg_sha = hashlib.sha256(jpeg_bytes).hexdigest().lower()
    print(f"  • Source JPEG Size: {len(jpeg_bytes)} bytes")
    print(f"  • Source SHA-256:   {expected_jpeg_sha}")

    # 2. Upload JPEG via POST /api/examinations
    print("\n[Step 2] Uploading JPEG via POST /api/examinations (multipart/form-data)...")
    files = {"file": ("forensic_sample_1.jpg", jpeg_bytes, "image/jpeg")}
    data = {
        "case_title": "Workflow Test: Disputed Image Registration",
        "case_reference": "CAS-WF-TEST-001",
        "purpose": "End-to-end forensic workflow verification",
        "evidence_source": "Direct acquisition test harness",
        "investigator": "Forensic Quality Auditor",
        "notes": "Automated workflow verification",
    }
    res = client.post("/api/examinations", data=data, files=files)
    assert res.status_code == 201, f"Failed: {res.text}"
    exam = res.json()
    print(f"  ✓ Ingestion HTTP Status: {res.status_code} Created")
    print(f"  ✓ Examination ID: {exam['id']}")
    print(f"  ✓ Evidence ID:    {exam['evidence_id']}")
    print(f"  ✓ Recorded Hash:  {exam['sha256_hash']}")

    # 3. Verify SHA-256 integrity
    assert exam["sha256_hash"].lower() == expected_jpeg_sha, "SHA-256 hash mismatch!"
    print(f"  ✓ Cryptographic SHA-256 integrity confirmed (exact match).")

    # 4. Verify evidence vault preservation
    ev_res = client.get(f"/api/evidence/{exam['evidence_id']}")
    assert ev_res.status_code == 200
    ev_data = ev_res.json()
    vault_file = settings.VAULT_DIR / ev_data["stored_filename"]
    assert vault_file.exists(), "Vault file does not exist!"
    with open(vault_file, "rb") as f:
        stored_bytes = f.read()
    assert stored_bytes == jpeg_bytes, "Stored bytes in vault do not match uploaded bytes!"
    print(f"  ✓ Vault pristine preservation verified ({len(stored_bytes)} bytes untouched).")

    # 5. Verify screening checks
    detail_res = client.get(f"/api/examinations/{exam['id']}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["status"] == "COMPLETED"
    print(f"  ✓ Examination status: {detail['status']}")
    print(f"  ✓ Findings count:     {len(detail['findings'])}")

    ela_res = client.get(f"/api/examinations/{exam['id']}/ela")
    assert ela_res.status_code == 200
    ela_data = ela_res.json()
    assert ela_data["format_supported"] is True
    assert ela_data["artifact_id"] is not None
    print(f"  ✓ JPEG ELA executed: artifact={ela_data['artifact_id']}, Q={ela_data['quality']}")

    stats_res = client.get(f"/api/examinations/{exam['id']}/statistics")
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert len(stats_data["rgb_statistics"]["histogram"]) == 32
    print(f"  ✓ Statistics computed: Laplacian focus variance={stats_data['spatial_noise']['laplacian_variance']}")

    ver_res = client.post(f"/api/evidence/{exam['evidence_id']}/verify")
    assert ver_res.status_code == 200
    assert ver_res.json()["status"] == "VERIFIED"
    print(f"  ✓ Layer 2 Re-verification check: {ver_res.json()['status']}")

    # 6. Test PNG Upload via POST /api/evidence
    print("\n[Step 3] Testing Lossless PNG Ingestion via POST /api/evidence...")
    png_img = Image.new("RGBA", (200, 200), color=(30, 180, 90, 255))
    png_buf = io.BytesIO()
    png_img.save(png_buf, format="PNG")
    png_bytes = png_buf.getvalue()
    expected_png_sha = hashlib.sha256(png_bytes).hexdigest().lower()

    png_files = {"file": ("lossless_chart.png", png_bytes, "image/png")}
    png_data = {"case_title": "PNG Registration Inquest"}
    res_png = client.post("/api/evidence", data=png_data, files=png_files)
    assert res_png.status_code == 201, f"Failed: {res_png.text}"
    exam_png = res_png.json()
    assert exam_png["sha256_hash"].lower() == expected_png_sha
    print(f"  ✓ PNG Ingested via /api/evidence. Hash: {exam_png['sha256_hash']}")

    # Check ELA on PNG
    ela_png = client.get(f"/api/examinations/{exam_png['id']}/ela").json()
    assert ela_png["format_supported"] is False
    assert "JPEG-specific" in ela_png["notes"]
    print(f"  ✓ PNG ELA cleanly reported as unsupported: \"{ela_png['notes'][:70]}...\"")

    print("\n======================================================================")
    print("SUCCESS: Complete End-to-End Workflow Verified Successfully!")
    print("======================================================================")

if __name__ == "__main__":
    test_full_workflow()
