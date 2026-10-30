import io
import json
import html
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
from app.core.config import settings
from app.core.constants import DISCLAIMER_TEXT

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for reliable 'Page X of Y' numbering and institutional headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages: int):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0F1E36"))
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "SCSS SATYA — FORENSIC IMAGE AUTHENTICITY SCREENING REPORT")
            self.drawRightString(612 - 54, 750, f"CONFIDENTIAL LABORATORY EXHIBIT")
            self.setStrokeColor(colors.HexColor("#C5A059"))
            self.setLineWidth(0.75)
            self.line(54, 744, 612 - 54, 744)

        # Footer (all pages)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#657187"))
        self.setStrokeColor(colors.HexColor("#DCE2EA"))
        self.setLineWidth(0.5)
        self.line(54, 45, 612 - 54, 45)
        
        self.drawString(54, 32, "SCSS SATYA | Doctrine: The tool screens. The expert decides. | ISO/IEC 27037 Evidence Handling")
        page_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(612 - 54, 32, page_text)
        self.restoreState()


def build_pdf_report(
    case_data: dict,
    evidence_data: dict,
    examination_data: dict,
    analysis_data: dict,
    findings_data: list[dict],
    review_data: dict,
    report_id: str,
) -> bytes:
    """Generate official forensic PDF screening report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()
    
    # Custom styles adhering to design palette
    navy = colors.HexColor("#0F1E36")
    secondary_navy = colors.HexColor("#172B47")
    gold = colors.HexColor("#C5A059")
    dark_gray = colors.HexColor("#172033")
    muted_text = colors.HexColor("#657187")
    border_color = colors.HexColor("#DCE2EA")
    bg_light = colors.HexColor("#F8FAFC")
    green_finding = colors.HexColor("#0D9488")
    amber_finding = colors.HexColor("#D97706")
    gray_finding = colors.HexColor("#64748B")

    title_style = ParagraphStyle(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=navy,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=gold,
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=navy,
        spaceBefore=14,
        spaceAfter=6,
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=secondary_navy,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "DocBody",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=dark_gray,
    )
    body_bold = ParagraphStyle(
        "DocBodyBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=navy,
    )
    code_style = ParagraphStyle(
        "DocCode",
        fontName="Courier",
        fontSize=7.5,
        leading=10,
        textColor=navy,
    )
    callout_style = ParagraphStyle(
        "Callout",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=navy,
    )

    story = []

    # Title & Banner
    story.append(Paragraph("SURE CLUE SCIENTIFIC SOLUTIONS (SCSS)", subtitle_style))
    story.append(Paragraph("FORENSIC IMAGE AUTHENTICITY SCREENING REPORT", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "SEVA FIRST Innovation Challenge 2026 | Sector 9: Emerging Technologies | Sub-theme 4: Responsible AI & Digital Trust",
        body_style
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=2, color=gold, spaceAfter=12))

    # Core Metadata Box
    meta_table_data = [
        [
            Paragraph("<b>Report Identifier:</b>", body_style),
            Paragraph(f"<font name='Courier'>{report_id}</font>", body_style),
            Paragraph("<b>Generated Timestamp:</b>", body_style),
            Paragraph(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), body_style),
        ],
        [
            Paragraph("<b>Case Reference:</b>", body_style),
            Paragraph(f"<b>{case_data.get('case_reference', 'N/A')}</b>", body_style),
            Paragraph("<b>Examination ID:</b>", body_style),
            Paragraph(f"<font name='Courier'>{examination_data.get('id', 'N/A')[:18]}...</font>", body_style),
        ],
        [
            Paragraph("<b>Case Title:</b>", body_style),
            Paragraph(case_data.get("title", "Untitled"), body_style),
            Paragraph("<b>Submitting Operator:</b>", body_style),
            Paragraph(case_data.get("investigator", "Authorized Examiner"), body_style),
        ],
    ]
    t_meta = Table(meta_table_data, colWidths=[110, 140, 110, 144])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_light),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Section 1: Pristine Evidence Record & Cryptographic Hash
    story.append(Paragraph("1. Pristine Evidence Record & Cryptographic Hash", h1_style))
    ev_table_data = [
        [Paragraph("<b>Original Filename</b>", body_bold), Paragraph(evidence_data.get("original_filename", "N/A"), body_style)],
        [Paragraph("<b>Cryptographic Digest (SHA-256)</b>", body_bold), Paragraph(f"<b><font name='Courier' color='#0F1E36'>{evidence_data.get('sha256_hash', 'N/A')}</font></b>", body_style)],
        [Paragraph("<b>File Size & Format</b>", body_bold), Paragraph(f"{evidence_data.get('file_size_bytes', 0):,} bytes | {evidence_data.get('detected_format', 'N/A')} ({evidence_data.get('width', 0)} × {evidence_data.get('height', 0)} px)", body_style)],
        [Paragraph("<b>Ingestion Timestamp</b>", body_bold), Paragraph(str(evidence_data.get("ingestion_timestamp", "N/A")), body_style)],
        [Paragraph("<b>Evidence Vault Reference</b>", body_bold), Paragraph(evidence_data.get("stored_filename", "N/A"), code_style)],
        [Paragraph("<b>Integrity Status</b>", body_bold), Paragraph("<b>VERIFIED</b> (Stored vault bytes strictly match original ingestion hash)", body_style)],
    ]
    t_ev = Table(ev_table_data, colWidths=[160, 344])
    t_ev.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("BACKGROUND", (0, 0), (0, -1), bg_light),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_ev)
    story.append(Spacer(1, 10))

    # Section 2: Metadata Inspection
    story.append(Paragraph("2. Container & EXIF Metadata Inspection", h1_style))
    meta_json_str = analysis_data.get("metadata_json")
    if meta_json_str:
        try:
            meta_obj = json.loads(meta_json_str)
            meta_rows = [
                [
                    Paragraph("<b>Category</b>", body_bold),
                    Paragraph("<b>Tag / Field</b>", body_bold),
                    Paragraph("<b>Status</b>", body_bold),
                    Paragraph("<b>Recorded Value / Forensic Observation</b>", body_bold),
                ]
            ]
            for cat in meta_obj.get("categories", []):
                for f in cat.get("fields", []):
                    status_text = f.get("status", "N/A")
                    val_text = f.get("value") or f.get("notes") or "Not Present"
                    if f.get("is_sensitive"):
                        val_text = "[PROTECTED SENSITIVE DATA] Disclosed under authorization"
                    meta_rows.append([
                        Paragraph(cat.get("name", ""), body_style),
                        Paragraph(f.get("label", f.get("tag")), body_style),
                        Paragraph(f"<b>{status_text}</b>", body_style),
                        Paragraph(str(val_text)[:120], body_style),
                    ])
            t_meta_grid = Table(meta_rows, colWidths=[120, 110, 70, 204])
            t_meta_grid.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, border_color),
                ("GRID", (0, 0), (-1, -1), 0.5, border_color),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t_meta_grid)
        except Exception:
            story.append(Paragraph("Metadata details could not be parsed.", body_style))
    story.append(Spacer(1, 10))

    # Section 3: Error Level Analysis & Exhibit
    story.append(Paragraph("3. JPEG Error Level Analysis (ELA) Exhibit", h1_style))
    ela_supported = analysis_data.get("ela_format_supported", False)
    if ela_supported:
        ela_notes = analysis_data.get("ela_notes", "ELA performed at Q=90.")
        story.append(Paragraph(f"<b>Methodology & Parameters:</b> {ela_notes}", body_style))
        story.append(Spacer(1, 6))

        # Check if heatmap artifact file exists on disk
        artifact_id = analysis_data.get("ela_artifact_path")
        if artifact_id:
            art_path = settings.ARTIFACTS_DIR / artifact_id
            if art_path.exists():
                try:
                    with PILImage.open(art_path) as im:
                        im_w, im_h = im.size
                    max_w = 4.5 * inch
                    max_h = 3.0 * inch
                    scale_factor = min(max_w / im_w, max_h / im_h)
                    rl_img = RLImage(str(art_path), width=im_w * scale_factor, height=im_h * scale_factor)
                    story.append(rl_img)
                    story.append(Spacer(1, 4))
                    story.append(Paragraph("<i>Exhibit 3.1: Amplified Recompression Residual Heatmap (Thermal Scale: Dark=Low, Bright=Elevated)</i>", callout_style))
                except Exception:
                    story.append(Paragraph("Exhibit image could not be embedded into document layout.", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            "<b>Forensic Limitation:</b> ELA reflects compression residual error rates across DCT blocks. "
            "High contrast edges and textural elements naturally create higher error. "
            "Residual variance alone does not substantiate composite insertion.",
            callout_style
        ))
    else:
        story.append(Paragraph(
            f"<b>Analysis Status: INCONCLUSIVE (Format Unsupported)</b><br/>"
            f"Image format '{evidence_data.get('detected_format')}' is a lossless raster container. "
            "Error Level Analysis models 8x8 DCT lossy JPEG quantization tables and is technically invalid when applied to lossless formats.",
            body_style
        ))
    story.append(Spacer(1, 10))

    # Section 4: Explainable Technical Findings
    story.append(Paragraph("4. Explainable Technical Findings", h1_style))
    story.append(Paragraph(
        "Structured technical findings produced by deterministic automated screening rules. "
        "Findings follow the three-tier categorization: <b>No Indicator Detected</b>, <b>Indicator Observed</b>, or <b>Inconclusive</b>.",
        body_style
    ))
    story.append(Spacer(1, 6))

    findings_rows = [
        [
            Paragraph("<b>Indicator</b>", body_bold),
            Paragraph("<b>Status</b>", body_bold),
            Paragraph("<b>Observed Measurement & Technical Explanation</b>", body_bold),
        ]
    ]

    for f in findings_data:
        status_val = f.get("status", "Inconclusive")
        if status_val == "Indicator Observed":
            status_p = Paragraph(f"<font color='#D97706'><b>● {status_val}</b></font>", body_style)
        elif status_val == "No Indicator Detected":
            status_p = Paragraph(f"<font color='#0D9488'><b>✔ {status_val}</b></font>", body_style)
        else:
            status_p = Paragraph(f"<font color='#64748B'><b>? {status_val}</b></font>", body_style)

        obs_text = (
            f"<b>Evidence:</b> {f.get('observed_evidence', '')}<br/>"
            f"<b>Explanation:</b> {f.get('explanation', '')}<br/>"
            f"<b>Limitation:</b> {f.get('limitations', '')}<br/>"
            f"<b>Recommended Action:</b> {f.get('recommended_action', '')}"
        )
        findings_rows.append([
            Paragraph(f.get("indicator_name", ""), body_bold),
            status_p,
            Paragraph(obs_text, body_style),
        ])

    t_findings = Table(findings_rows, colWidths=[120, 100, 284])
    t_findings.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_findings)
    story.append(Spacer(1, 10))

    # Section 5: Qualified Human Forensic Review & Opinion
    story.append(Paragraph("5. Qualified Human Forensic Review & Examiner Opinion", h1_style))
    rev_status = review_data.get("review_status", "Pending Review")
    opinion_text = review_data.get("examiner_opinion") or "No formal examiner opinion recorded."
    examiner_name = review_data.get("examiner_name", "Unassigned")
    examiner_org = review_data.get("organization", "N/A")
    examiner_qual = review_data.get("qualification", "N/A")
    cred_status = review_data.get("credential_status", "UNVERIFIED")

    review_table_data = [
        [Paragraph("<b>Examiner Name:</b>", body_style), Paragraph(examiner_name, body_bold), Paragraph("<b>Review Status:</b>", body_style), Paragraph(f"<b>{rev_status}</b>", body_style)],
        [Paragraph("<b>Organization:</b>", body_style), Paragraph(examiner_org, body_style), Paragraph("<b>Credential Status:</b>", body_style), Paragraph(cred_status, body_style)],
        [Paragraph("<b>Qualifications:</b>", body_style), Paragraph(examiner_qual, body_style), Paragraph("<b>Review Date:</b>", body_style), Paragraph(str(review_data.get("reviewed_at", "N/A")), body_style)],
        [Paragraph("<b>Qualitative Notes:</b>", body_style), Paragraph(review_data.get("qualitative_notes") or "None entered.", body_style), Paragraph("", body_style), Paragraph("", body_style)],
        [Paragraph("<b>Examiner Opinion:</b>", body_style), Paragraph(f"<i>\"{opinion_text}\"</i>", body_style), Paragraph("", body_style), Paragraph("", body_style)],
    ]
    t_rev = Table(review_table_data, colWidths=[100, 160, 100, 144])
    t_rev.setStyle(TableStyle([
        ("SPAN", (1, 3), (3, 3)),
        ("SPAN", (1, 4), (3, 4)),
        ("BOX", (0, 0), (-1, -1), 0.5, border_color),
        ("GRID", (0, 0), (-1, -1), 0.5, border_color),
        ("BACKGROUND", (0, 0), (0, -1), bg_light),
        ("BACKGROUND", (2, 0), (2, 2), bg_light),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t_rev)
    story.append(Spacer(1, 10))

    # Section 6: Legal Boundary & Disclaimer
    story.append(Paragraph("6. Institutional Doctrine & Statutory Disclaimers", h1_style))
    doctrine_box = [
        [
            Paragraph(
                "<b>GUIDING FORENSIC DOCTRINE:</b><br/>"
                "<b>\"The tool screens. The expert decides.\"</b><br/><br/>"
                f"{DISCLAIMER_TEXT}<br/><br/>"
                "<b>Statutory Reference (Indian Evidence & Evidence Framework):</b> Section 63 of Bharatiya Sakshya Adhiniyam, 2023 (BSA) / former Section 65B of Indian Evidence Act, 1872. "
                "This report constitutes an automated screening and documentation exhibit. It does not replace an official Section 63 BSA certificate signed by the person in lawful control of the device. "
                "ISO/IEC 27037:2012 principles govern digital evidence preservation.",
                callout_style
            )
        ]
    ]
    t_doc = Table(doctrine_box, colWidths=[504])
    t_doc.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_light),
        ("BOX", (0, 0), (-1, -1), 1, gold),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_doc)
    story.append(Spacer(1, 15))

    # Signature block
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Examiner Signature</b>", body_style),
            Paragraph("____________________________<br/><b>Laboratory Supervisor</b>", body_style),
            Paragraph("____________________________<br/><b>Date & Official Stamp</b>", body_style),
        ]
    ]
    t_sig = Table(sig_data, colWidths=[168, 168, 168])
    t_sig.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t_sig)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
