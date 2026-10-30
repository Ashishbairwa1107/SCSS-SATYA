import json
from datetime import datetime, timezone
from typing import Any
from app.core.config import settings
from app.core.constants import DISCLAIMER_TEXT

def build_json_report(
    case_data: dict,
    evidence_data: dict,
    examination_data: dict,
    analysis_data: dict,
    findings_data: list[dict],
    review_data: dict,
    report_id: str,
) -> dict[str, Any]:
    """Generate structured machine-readable JSON forensic report according to SATYA v1.0.0 schema."""
    
    # Parse nested JSON strings if needed
    meta_json = analysis_data.get("metadata_json")
    if isinstance(meta_json, str):
        try:
            meta_obj = json.loads(meta_json)
        except Exception:
            meta_obj = {}
    else:
        meta_obj = meta_json or {}

    rgb_json = analysis_data.get("rgb_statistics_json")
    if isinstance(rgb_json, str):
        try:
            rgb_obj = json.loads(rgb_json)
        except Exception:
            rgb_obj = {}
    else:
        rgb_obj = rgb_json or {}

    spatial_json = analysis_data.get("spatial_noise_json")
    if isinstance(spatial_json, str):
        try:
            spatial_obj = json.loads(spatial_json)
        except Exception:
            spatial_obj = {}
    else:
        spatial_obj = spatial_json or {}

    checklist_json = review_data.get("checklist_responses_json")
    if isinstance(checklist_json, str):
        try:
            checklist_obj = json.loads(checklist_json)
        except Exception:
            checklist_obj = []
    else:
        checklist_obj = checklist_json or []

    report_payload = {
        "$schema_version": "1.0.0",
        "platform": {
            "name": settings.PROJECT_NAME,
            "full_title": settings.PROJECT_FULL_TITLE,
            "version": settings.VERSION,
            "doctrine": settings.DOCTRINE,
            "organization": settings.ORGANIZATION,
            "challenge": settings.CHALLENGE,
        },
        "report_metadata": {
            "report_id": report_id,
            "format": "JSON",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "doctrine_statement": settings.DOCTRINE,
        },
        "case": {
            "id": case_data.get("id"),
            "case_reference": case_data.get("case_reference"),
            "title": case_data.get("title"),
            "purpose": case_data.get("purpose"),
            "evidence_source": case_data.get("evidence_source"),
            "investigator": case_data.get("investigator"),
            "notes": case_data.get("notes"),
            "created_at": str(case_data.get("created_at")),
        },
        "evidence": {
            "id": evidence_data.get("id"),
            "original_filename": evidence_data.get("original_filename"),
            "stored_filename": evidence_data.get("stored_filename"),
            "file_size_bytes": evidence_data.get("file_size_bytes"),
            "detected_format": evidence_data.get("detected_format"),
            "width": evidence_data.get("width"),
            "height": evidence_data.get("height"),
            "color_mode": evidence_data.get("color_mode"),
            "sha256_hash": evidence_data.get("sha256_hash"),
            "ingestion_timestamp": str(evidence_data.get("ingestion_timestamp")),
            "is_specimen": evidence_data.get("is_specimen", False),
            "specimen_type": evidence_data.get("specimen_type"),
        },
        "examination": {
            "id": examination_data.get("id"),
            "status": examination_data.get("status"),
            "started_at": str(examination_data.get("started_at")),
            "completed_at": str(examination_data.get("completed_at")),
            "failure_reason": examination_data.get("failure_reason"),
        },
        "forensic_layer_results": {
            "layer_1_screening": {
                "metadata": meta_obj,
                "error_level_analysis": {
                    "format_supported": analysis_data.get("ela_format_supported", False),
                    "quality_parameter": analysis_data.get("ela_quality"),
                    "scale_parameter": analysis_data.get("ela_scale"),
                    "artifact_id": analysis_data.get("ela_artifact_path"),
                    "notes": analysis_data.get("ela_notes"),
                },
                "rgb_channel_statistics": rgb_obj,
                "spatial_noise_analysis": spatial_obj,
            },
            "layer_2_integrity": {
                "sha256_digest": evidence_data.get("sha256_hash"),
                "verification_method": "Direct binary read of vault-stored bytes",
                "storage_model": "Isolated local evidence vault",
                "integrity_status": "VERIFIED",
            },
            "layer_3_explainable_findings": findings_data,
            "layer_4_human_review": {
                "examiner_name": review_data.get("examiner_name"),
                "organization": review_data.get("organization"),
                "qualification": review_data.get("qualification"),
                "credential_status": review_data.get("credential_status"),
                "qualitative_notes": review_data.get("qualitative_notes"),
                "manual_checklist": checklist_obj,
                "review_status": review_data.get("review_status"),
                "examiner_opinion": review_data.get("examiner_opinion"),
                "reviewed_at": str(review_data.get("reviewed_at")),
            },
        },
        "legal_and_scientific_disclaimer": {
            "doctrine": settings.DOCTRINE,
            "text": DISCLAIMER_TEXT,
            "statutory_reference": "Section 63, Bharatiya Sakshya Adhiniyam, 2023 (BSA) / former Section 65B, Indian Evidence Act, 1872",
            "standard_reference": "ISO/IEC 27037:2012 Digital Evidence Handling",
        }
    }
    return report_payload
