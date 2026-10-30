from enum import Enum

class FindingStatus(str, Enum):
    NO_INDICATOR = "No Indicator Detected"
    INDICATOR_OBSERVED = "Indicator Observed"
    INCONCLUSIVE = "Inconclusive"

class ReviewStatus(str, Enum):
    PENDING_REVIEW = "Pending Review"
    UNDER_REVIEW = "Under Review"
    REVIEWED_NO_OPINION = "Reviewed — No Final Opinion"
    OPINION_RECORDED = "Examiner Opinion Recorded"

class IntegrityStatus(str, Enum):
    VERIFIED = "VERIFIED"
    MISMATCH = "MISMATCH"
    UNVERIFIED = "UNVERIFIED"

class ExaminationStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AuditEventType(str, Enum):
    EVIDENCE_INGESTED = "EVIDENCE_INGESTED"
    EXAMINATION_STARTED = "EXAMINATION_STARTED"
    EXAMINATION_COMPLETED = "EXAMINATION_COMPLETED"
    EXAMINATION_FAILED = "EXAMINATION_FAILED"
    INTEGRITY_VERIFIED = "INTEGRITY_VERIFIED"
    INTEGRITY_FAILED = "INTEGRITY_FAILED"
    REPORT_GENERATED = "REPORT_GENERATED"
    EXAMINER_REVIEW_SAVED = "EXAMINER_REVIEW_SAVED"
    SPECIMEN_GENERATED = "SPECIMEN_GENERATED"

# Mandatory manual verification checklist items
STANDARD_VERIFICATION_CHECKLIST = [
    {
        "id": "chk_source_context",
        "label": "Original Source & Acquisition Context",
        "description": "Assess image provenance, transmission history, camera model, and device chain of custody.",
    },
    {
        "id": "chk_raw_file",
        "label": "Camera RAW / Original Master Availability",
        "description": "Verify whether original uncompressed camera sensor file (RAW, DNG, CR2, NEF) is available for baseline comparison.",
    },
    {
        "id": "chk_metadata_consistency",
        "label": "Metadata Consistency & Provenance",
        "description": "Evaluate EXIF/IPTC/XMP timestamps, make, model, software trace tags, and device consistency.",
    },
    {
        "id": "chk_compression_history",
        "label": "Compression & Generation History",
        "description": "Examine recompression characteristics, quantization tables, and potential social media stripping.",
    },
    {
        "id": "chk_ela_analysis",
        "label": "Error Level Analysis (ELA) Contextual Review",
        "description": "Evaluate high-contrast edges vs genuine compression anomalies; verify alternative explanations.",
    },
    {
        "id": "chk_spatial_noise",
        "label": "Spatial Noise & Geometry Inspection",
        "description": "Inspect channel noise variance, pixel gradients, lighting coherence, and geometric perspective consistency.",
    },
    {
        "id": "chk_corroborating_evidence",
        "label": "Corroborating Records & Multi-Shot Series",
        "description": "Cross-reference against surrounding scene captures, burst captures, or independent witness records.",
    },
    {
        "id": "chk_independent_verification",
        "label": "Independent Technical Re-Verification",
        "description": "Confirm observations across isolated forensic workstations or complementary algorithmic tools.",
    },
    {
        "id": "chk_chain_of_custody",
        "label": "Chain of Custody & Hash Preservation",
        "description": "Validate that SHA-256 evidence record remains unbroken since time of acquisition.",
    },
    {
        "id": "chk_specialist_referral",
        "label": "Specialist Forensic Laboratory Referral",
        "description": "Determine if full sensor PRNU, physical optical bench, or judicial forensic laboratory certification is required.",
    },
]

DISCLAIMER_TEXT = (
    "These findings represent technical screening observations. The absence of detected indicators "
    "does not establish authenticity, and observed anomalies may have legitimate explanations. "
    "SCSS SATYA is a forensic screening and documentation prototype, not a certified forensic laboratory instrument. "
    "The tool screens. The expert decides."
)
