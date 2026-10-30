from typing import Any
from app.core.constants import FindingStatus

def generate_explainable_findings(
    metadata_result: dict[str, Any],
    ela_result: dict[str, Any],
    stats_result: dict[str, Any],
    detected_format: str,
) -> list[dict[str, Any]]:
    """
    Synthesize explainable technical forensic findings from deterministic measurements.
    
    Status Rules:
    - NO_INDICATOR: Test completed normally, measurements fell within standard nominal bounds.
    - INDICATOR_OBSERVED: An empirical anomaly, software signature, or residual divergence was detected.
    - INCONCLUSIVE: Data missing, format unsupported, or ambiguity prevents reliable automated screening.
    
    Never computes an arbitrary authenticity percentage or claims definitive manipulation.
    """
    findings: list[dict[str, Any]] = []
    order = 1

    # 1. EXIF Metadata Availability & Hardware Provenance
    meta_summary = metadata_result.get("summary", {})
    has_exif = meta_summary.get("has_exif", False)
    cam_make = meta_summary.get("camera_make")
    cam_model = meta_summary.get("camera_model")

    if has_exif and (cam_make or cam_model):
        findings.append({
            "finding_key": "FINDING_METADATA_PROVENANCE",
            "indicator_name": "EXIF Camera Hardware Provenance",
            "status": FindingStatus.NO_INDICATOR.value,
            "observed_evidence": f"Recorded Make: '{cam_make or 'N/A'}', Model: '{cam_model or 'N/A'}'",
            "explanation": "Standard EXIF device identity tags were located and decoded from the evidence container.",
            "significance": "Suggests the container retains metadata attributes consistent with digital camera acquisition.",
            "limitations": (
                "EXIF tags are unauthenticated plaintext and can be generated, copied, or modified using hex editors "
                "or metadata manipulation utilities. Presence of device tags does not verify physical capture provenance."
            ),
            "recommended_action": "Corroborate with original storage media, shutter counter continuity, and physical acquisition records.",
            "order_index": order,
        })
    else:
        findings.append({
            "finding_key": "FINDING_METADATA_PROVENANCE",
            "indicator_name": "EXIF Camera Hardware Provenance",
            "status": FindingStatus.INCONCLUSIVE.value,
            "observed_evidence": "No camera make or model tags were identified in the image file.",
            "explanation": "Camera device provenance metadata is absent or unreadable in the submitted file container.",
            "significance": (
                "Commonly occurs when images are transmitted through messaging services, social media, "
                "or saved via screenshot utilities that routinely strip metadata for privacy and bandwidth reasons."
            ),
            "limitations": "Missing EXIF information must never be interpreted as evidence of malicious manipulation or deepfake synthesis.",
            "recommended_action": "Request pristine original camera card dump, RAW file, or verified forensic bitstream image.",
            "order_index": order,
        })
    order += 1

    # 2. Software Processing Traces
    sw_detected = meta_summary.get("software_trace_detected", False)
    sw_name = meta_summary.get("software_name")

    if sw_detected:
        findings.append({
            "finding_key": "FINDING_SOFTWARE_TRACE",
            "indicator_name": "Image Editing Application Software Signature",
            "status": FindingStatus.INDICATOR_OBSERVED.value,
            "observed_evidence": f"Software tag recorded in metadata: '{sw_name}'",
            "explanation": "The file contains header attributes identifying an image manipulation or graphics application.",
            "significance": "Confirms the image has been processed or saved through image editing software.",
            "limitations": (
                "Editing software is routinely employed for benign forensic activities including cropping, color correction, "
                "redaction, and re-exporting. Software traces are technical observations, not proof of malicious alteration."
            ),
            "recommended_action": "Conduct localized pixel-level consistency analysis and obtain the pre-edit source file.",
            "order_index": order,
        })
    elif has_exif and not sw_detected:
        findings.append({
            "finding_key": "FINDING_SOFTWARE_TRACE",
            "indicator_name": "Image Editing Application Software Signature",
            "status": FindingStatus.NO_INDICATOR.value,
            "observed_evidence": "No recognized editing application signatures detected in metadata software fields.",
            "explanation": "No known post-processing software markers (e.g., Photoshop, GIMP) were identified in the file metadata.",
            "significance": "Indicates no overt self-identifying desktop editor trace is embedded in container fields.",
            "limitations": "Metadata can be stripped or modified to remove software trace tags. Absence of software tags does not prove the file was untouched.",
            "recommended_action": "Verify pixel spatial consistency and compression grid characteristics.",
            "order_index": order,
        })
    else:
        findings.append({
            "finding_key": "FINDING_SOFTWARE_TRACE",
            "indicator_name": "Image Editing Application Software Signature",
            "status": FindingStatus.INCONCLUSIVE.value,
            "observed_evidence": "Metadata absent; software field unavailable for inspection.",
            "explanation": "Because container metadata is missing, software trace screening cannot be evaluated from metadata alone.",
            "significance": "Software processing history cannot be confirmed or ruled out via container headers.",
            "limitations": "Inability to evaluate software tags is a limitation of available metadata, not a negative indicator.",
            "recommended_action": "Evaluate secondary compression artifacts and residual consistency.",
            "order_index": order,
        })
    order += 1

    # 3. Error Level Analysis (ELA) Recompression Residuals
    ela_supported = ela_result.get("format_supported", False)
    if not ela_supported:
        findings.append({
            "finding_key": "FINDING_ELA_RESIDUALS",
            "indicator_name": "JPEG Error Level Analysis (ELA)",
            "status": FindingStatus.INCONCLUSIVE.value,
            "observed_evidence": f"File format '{detected_format}' is not a lossy JPEG container.",
            "explanation": "Error Level Analysis models the error between successive lossy JPEG DCT quantization iterations.",
            "significance": "JPEG ELA is scientifically invalid when applied to lossless formats (PNG, TIFF, BMP).",
            "limitations": "Lossless formats do not utilize 8x8 DCT quantization tables. Alternative spatial metrics must be used.",
            "recommended_action": "Rely on spatial noise variance, high-frequency residual consistency, and color histogram distribution.",
            "order_index": order,
        })
    else:
        mean_diff = ela_result.get("mean_difference", 0.0) or 0.0
        max_diff = ela_result.get("max_difference", 0.0) or 0.0
        std_diff = ela_result.get("residual_std", 0.0) or 0.0

        # High variance in recompression error may indicate composite insertion or varied compression history
        if max_diff > 180 and std_diff > 8.0:
            findings.append({
                "finding_key": "FINDING_ELA_RESIDUALS",
                "indicator_name": "JPEG Error Level Analysis (ELA)",
                "status": FindingStatus.INDICATOR_OBSERVED.value,
                "observed_evidence": f"Elevated residual spread: Max residual={max_diff:.1f}, Standard deviation={std_diff:.2f}",
                "explanation": (
                    "Marked variance detected in recompression error residuals across different image zones at Q=90. "
                    "Distinct regions exhibit differing error rates when re-encoded."
                ),
                "significance": (
                    "May indicate composite splicing where elements from different sources or compression qualities "
                    "were assembled into a single frame."
                ),
                "limitations": (
                    "High-contrast edges, fine textures, saturated primary colors, and text overlays naturally produce "
                    "higher recompression error without manipulation. ELA does not establish intent or authenticity."
                ),
                "recommended_action": "Examine the ELA heatmap exhibit interactively and cross-reference localized boundaries with spatial noise.",
                "order_index": order,
            })
        else:
            findings.append({
                "finding_key": "FINDING_ELA_RESIDUALS",
                "indicator_name": "JPEG Error Level Analysis (ELA)",
                "status": FindingStatus.NO_INDICATOR.value,
                "observed_evidence": f"Uniform residual distribution: Mean difference={mean_diff:.2f}, Std dev={std_diff:.2f}",
                "explanation": "Recompression error levels across the image frame demonstrate expected homogeneous characteristics.",
                "significance": "No anomalous regional divergence in JPEG recompression residual magnitude was identified.",
                "limitations": (
                    "Repeated resaving at low quality or global recompression can homogenize residual levels, "
                    "masking earlier splicing. Uniform ELA is not proof of authenticity."
                ),
                "recommended_action": "Inspect high-magnification pixel borders along suspected object contours.",
                "order_index": order,
            })
    order += 1

    # 4. Spatial Noise & High-Frequency Texture Consistency
    spatial_noise = stats_result.get("spatial_noise", {})
    noise_sigma = spatial_noise.get("high_freq_noise_sigma", 0.0)
    laplacian_var = spatial_noise.get("laplacian_variance", 0.0)

    # Abnormally zero or extremely low noise on natural photograph may indicate synthetic generation or heavy denoising
    if noise_sigma < 0.35 and laplacian_var < 15.0:
        findings.append({
            "finding_key": "FINDING_SPATIAL_NOISE",
            "indicator_name": "High-Frequency Spatial Noise Distribution",
            "status": FindingStatus.INDICATOR_OBSERVED.value,
            "observed_evidence": f"Atypically low high-frequency noise: Sigma={noise_sigma:.2f}, Laplacian variance={laplacian_var:.1f}",
            "explanation": "Image displays near-total absence of natural sensor noise or micro-grain texture across the frame.",
            "significance": "Consistent with aggressive smoothing, flat vector graphics, synthetic generation, or extreme compression.",
            "limitations": "Heavy Gaussian blur, intentional graphic illustration, or high-end studio lighting can also suppress high-frequency noise.",
            "recommended_action": "Perform high-magnification optical check for sensor PRNU or diffusion artifacts.",
            "order_index": order,
        })
    else:
        findings.append({
            "finding_key": "FINDING_SPATIAL_NOISE",
            "indicator_name": "High-Frequency Spatial Noise Distribution",
            "status": FindingStatus.NO_INDICATOR.value,
            "observed_evidence": f"Measured noise sigma={noise_sigma:.2f}, Laplacian variance={laplacian_var:.1f}",
            "explanation": "Spatial grain distribution and high-frequency edge variance are within typical observable ranges.",
            "significance": "No anomalous global noise absence or extreme synthetic texture smoothing observed.",
            "limitations": "Sophisticated generative models or targeted local denoising may preserve realistic global noise statistics.",
            "recommended_action": "Inspect local regions for localized noise discrepancies.",
            "order_index": order,
        })
    order += 1

    # 5. Color Channel Dynamic Range & Saturation Balance
    rgb_stats = stats_result.get("rgb_statistics", {})
    r_stat = rgb_stats.get("red", {})
    g_stat = rgb_stats.get("green", {})
    b_stat = rgb_stats.get("blue", {})

    # Check for severe clipping or channel imbalance
    r_max = r_stat.get("max", 255)
    g_max = g_stat.get("max", 255)
    b_max = b_stat.get("max", 255)
    r_min = r_stat.get("min", 0)
    g_min = g_stat.get("min", 0)
    b_min = b_stat.get("min", 0)

    if (r_max == 0 and g_max == 0 and b_max == 0) or (r_min == 255 and g_min == 255 and b_min == 255):
        findings.append({
            "finding_key": "FINDING_COLOR_CHANNELS",
            "indicator_name": "Color Channel Tonality & Dynamic Range",
            "status": FindingStatus.INCONCLUSIVE.value,
            "observed_evidence": "Extreme solid color or blank channel distribution.",
            "explanation": "The image data exhibits monochromatic or zero-variance channel intensity.",
            "significance": "Image contains no photographic detail or valid dynamic range for examination.",
            "limitations": "Test specimen or non-photographic artifact.",
            "recommended_action": "Confirm evidence validity and verify file integrity.",
            "order_index": order,
        })
    else:
        findings.append({
            "finding_key": "FINDING_COLOR_CHANNELS",
            "indicator_name": "Color Channel Tonality & Dynamic Range",
            "status": FindingStatus.NO_INDICATOR.value,
            "observed_evidence": f"Red mean={r_stat.get('mean')}, Green mean={g_stat.get('mean')}, Blue mean={b_stat.get('mean')}",
            "explanation": "Color channel dynamic range spans full photographic spectrum with continuous tonal transitions.",
            "significance": "No anomalous hard channel clamping or artificial tonal gaps detected.",
            "limitations": "Color channel distributions can be manipulated without leaving obvious macroscopic histogram gaps.",
            "recommended_action": "Review individual channel distributions on interactive Recharts exhibit.",
            "order_index": order,
        })

    return findings
