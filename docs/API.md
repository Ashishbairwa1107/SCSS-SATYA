# SCSS SATYA — REST API Documentation

Base URL: `http://127.0.0.1:8000/api`  
Swagger UI: `http://127.0.0.1:8000/docs`  
ReDoc: `http://127.0.0.1:8000/redoc`

---

## 1. System Endpoints

### `GET /api/health`
Performs live health screening of backend subsystems.
- **Response 200:**
  ```json
  {
    "status": "HEALTHY",
    "version": "1.0.0",
    "timestamp": "2026-10-29T11:00:00Z",
    "doctrine": "The tool screens. The expert decides.",
    "database_connected": true,
    "vault_accessible": true
  }
  ```

### `GET /api/system/info`
Returns platform specifications, max limits, supported formats, and doctrine.

### `GET /api/system/metrics`
Returns database-backed dashboard metrics: total examinations, evidence items, pending reviews, completed exams, and integrity failures.

---

## 2. Case Management Endpoints

### `POST /api/cases`
Creates a new forensic case container.
- **Payload:**
  ```json
  {
    "title": "Disputed Land Document Analysis",
    "case_reference": "CAS-20261029-A1B2",
    "purpose": "Screening document stamp authenticity",
    "evidence_source": "Seized USB drive",
    "investigator": "Dr. V. Rao",
    "notes": "Case #742/2026"
  }
  ```
- **Response 201:** `CaseResponse`

### `GET /api/cases`
Lists cases with search query, pagination (`skip`, `limit`), and counts of associated evidence and examinations.

### `GET /api/cases/{case_id}`
Retrieves specific case record.

---

## 3. Evidence & Ingestion Endpoints

### `POST /api/examinations`
Primary evidence ingestion and screening initiation endpoint.
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  - `file`: Raw binary image file (JPEG, PNG, TIFF, WEBP, BMP — up to 50 MB)
  - `case_title`: (Optional) Case title if creating new case
  - `case_reference`: (Optional) Custom case reference
  - `case_id`: (Optional) Associate with existing case
  - `purpose`: (Optional) Reason for examination
  - `evidence_source`: (Optional) Acquisition provenance
  - `investigator`: (Optional) Submitting examiner
  - `notes`: (Optional) Additional contextual remarks
- **Response 201:** `ExaminationResponse` with SHA-256 hash and screening summary.

### `GET /api/examinations`
Lists examinations with query filters:
- `search`: Case reference, title, or filename
- `format_filter`: E.g., `JPEG`, `PNG`
- `review_status`: E.g., `Pending Review`, `Examiner Opinion Recorded`
- `skip`, `limit`: Pagination controls

### `GET /api/examinations/{examination_id}`
Returns complete examination dossier including case metadata, evidence details, explainable findings, and examiner review state.

### `GET /api/examinations/{examination_id}/findings`
Returns ordered list of explainable findings conforming to the 3-tier status model.

---

## 4. Analysis Exhibits Endpoints

### `GET /api/examinations/{examination_id}/ela`
Returns JPEG Error Level Analysis parameters, residual statistics, and artifact exhibit URLs.

### `GET /api/examinations/{examination_id}/statistics`
Returns radiometric RGB channel statistics, 32-bin intensity histogram, and spatial noise measurements.

### `GET /api/evidence/{evidence_id}/original`
Downloads pristine unaltered evidence bytes directly from the storage vault.

### `POST /api/evidence/{evidence_id}/verify`
Executes Layer 2 integrity verification. Re-reads stored bytes from disk, computes SHA-256, and returns `VERIFIED` or `MISMATCH`.

### `GET /api/evidence/{evidence_id}/metadata`
Returns categorized EXIF/IPTC/TIFF metadata breakdown with Present/Missing/Unreadable statuses.

### `GET /api/evidence/artifacts/{filename}`
Streams derived visual analysis artifacts (ELA thermal heatmaps, grayscale exhibits).

---

## 5. Examiner Review Endpoints

### `GET /api/examinations/{examination_id}/review`
Returns examiner review dossier, manual checklist responses, qualifications, and opinions.

### `PUT /api/examinations/{examination_id}/review`
Updates human examiner review. Requires `confirm_opinion_disclosure=true` if recording an opinion. Logs audit event.

---

## 6. Official Forensic Reporting Endpoints

### `POST /api/examinations/{examination_id}/reports`
Generates an official forensic report in `PDF` (ReportLab 2-pass) or `JSON` format.
- **Payload:**
  ```json
  {
    "report_format": "PDF",
    "include_sensitive_gps": false
  }
  ```
- **Response 201:** `ReportResponse` with download URL and report SHA-256 hash.

### `GET /api/reports/{report_id}/pdf`
Downloads binary PDF report file.

### `GET /api/reports/{report_id}/json`
Downloads machine-readable JSON forensic report (Schema v1.0.0).

---

## 7. Demonstration Specimens Endpoints

- `POST /api/specimens/camera-style`: Generates Specimen A (natural landscape with synthetic EXIF).
- `POST /api/specimens/spliced-composite`: Generates Specimen B (structural composite with inserted region & GIMP tag).
- `POST /api/specimens/lossless-png`: Generates Specimen C (lossless calibration chart demonstrating honest ELA refusal).
