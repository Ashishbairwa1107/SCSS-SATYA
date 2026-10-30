import io
from pathlib import Path
from typing import Optional, Any
from PIL import Image, ImageChops, ImageEnhance
import numpy as np
import cv2
from app.core.config import settings
from app.services.storage import storage_service

def perform_error_level_analysis(
    file_bytes: bytes,
    detected_format: str,
    quality: int = 90,
    scale: int = 15,
) -> dict[str, Any]:
    """
    Error Level Analysis (ELA) for supported JPEG images.
    
    Methodology:
    1. Decode original image bytes into RGB representation.
    2. Save a temporary working copy in memory recompressed at Q={quality}.
    3. Reopen recompressed copy and compute absolute pixel difference:
       diff = |original_pixel - recompressed_pixel|
    4. Amplify difference by multiplier {scale} for human visual review.
    5. Save high-resolution ELA heatmap artifact in storage/artifacts.
    6. Compute statistical metrics (mean diff, std dev, max diff).

    For lossless or non-JPEG formats (PNG, TIFF, BMP), JPEG ELA is technically invalid.
    Returns honest explanatory status.
    """
    fmt = detected_format.upper()
    if fmt not in ["JPEG", "JPG"]:
        return {
            "format_supported": False,
            "quality": quality,
            "scale": scale,
            "artifact_id": None,
            "artifact_url": None,
            "grayscale_artifact_url": None,
            "notes": (
                f"ELA is a JPEG-specific recompression analysis technique. "
                f"The ingested image format is {detected_format}. In accordance with digital forensic standards, "
                f"JPEG recompression error level analysis is not applicable to lossless or non-JPEG formats."
            ),
            "mean_difference": None,
            "max_difference": None,
            "residual_std": None,
            "limitation_statement": (
                "JPEG ELA relies on standard DCT 8x8 block quantization variance between successive lossy compression cycles. "
                "Applying it to lossless formats produces artificial or invalid artifacts."
            )
        }

    try:
        # 1. Decode original image
        orig_img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        orig_np = np.array(orig_img, dtype=np.float32)

        # 2. Re-encode at documented quality setting
        recomp_buffer = io.BytesIO()
        orig_img.save(recomp_buffer, format="JPEG", quality=quality)
        recomp_buffer.seek(0)

        # 3. Re-read recompressed copy
        recomp_img = Image.open(recomp_buffer).convert("RGB")
        recomp_np = np.array(recomp_img, dtype=np.float32)

        # 4. Compute absolute difference per channel
        abs_diff = np.abs(orig_np - recomp_np)
        mean_diff = float(np.mean(abs_diff))
        max_diff = float(np.max(abs_diff))
        std_diff = float(np.std(abs_diff))

        # 5. Amplify difference by scale factor and clip to [0, 255]
        amplified = np.clip(abs_diff * scale, 0, 255).astype(np.uint8)

        # Grayscale representation of amplified residual
        gray_amplified = cv2.cvtColor(amplified, cv2.COLOR_RGB2GRAY)

        # Generate false-color thermal colormap (INFERNO) for intuitive anomaly inspection
        heatmap_bgr = cv2.applyColorMap(gray_amplified, cv2.COLORMAP_INFERNO)
        heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
        heatmap_img = Image.fromarray(heatmap_rgb)

        # Save heatmap artifact
        heat_buf = io.BytesIO()
        heatmap_img.save(heat_buf, format="PNG")
        heat_bytes = heat_buf.getvalue()
        artifact_filename, artifact_path = storage_service.save_artifact(
            heat_bytes, extension=".png", prefix="ela_heatmap"
        )

        # Save amplified grayscale exhibit artifact
        gray_img = Image.fromarray(gray_amplified)
        gray_buf = io.BytesIO()
        gray_img.save(gray_buf, format="PNG")
        gray_bytes = gray_buf.getvalue()
        gray_filename, gray_path = storage_service.save_artifact(
            gray_bytes, extension=".png", prefix="ela_gray"
        )

        # Build descriptive observation
        notes = (
            f"JPEG ELA executed at Q={quality} with {scale}x difference amplification. "
            f"Mean residual difference: {mean_diff:.2f}, standard deviation: {std_diff:.2f}, maximum residual: {max_diff:.1f}. "
            "High residual brightness indicates image areas that experienced greater error upon recompression, "
            "which frequently corresponds to high-frequency edges, texture transitions, or differing compression histories."
        )

        return {
            "format_supported": True,
            "quality": quality,
            "scale": scale,
            "artifact_id": artifact_filename,
            "artifact_url": f"/api/evidence/artifacts/{artifact_filename}",
            "grayscale_artifact_url": f"/api/evidence/artifacts/{gray_filename}",
            "notes": notes,
            "mean_difference": round(mean_diff, 3),
            "max_difference": round(max_diff, 1),
            "residual_std": round(std_diff, 3),
            "limitation_statement": (
                "ELA is not a universal or automated manipulation detector. "
                "Natural textural complexity, edge contrast, color saturation, and prior software exports all "
                "substantially modulate residual intensity. Bright ELA regions alone do not prove composite insertion."
            )
        }
    except Exception as exc:
        return {
            "format_supported": False,
            "quality": quality,
            "scale": scale,
            "artifact_id": None,
            "artifact_url": None,
            "grayscale_artifact_url": None,
            "notes": f"Error Level Analysis could not be completed: {str(exc)}",
            "mean_difference": None,
            "max_difference": None,
            "residual_std": None,
            "limitation_statement": "Execution failed during decoding or recompression step."
        }
