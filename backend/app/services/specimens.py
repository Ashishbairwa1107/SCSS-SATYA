import io
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ExifTags
import numpy as np
from app.core.config import settings

SPECIMENS_DIR = settings.STORAGE_DIR / "specimens"
SPECIMENS_DIR.mkdir(parents=True, exist_ok=True)

def generate_specimen_a_camera_photo() -> tuple[bytes, str, dict]:
    """
    Specimen A: Camera-Style Photograph (Synthetic Demonstration Specimen)
    Generates a natural landscape with atmospheric gradients, rolling hills, and sun,
    with embedded synthetic EXIF tags.
    """
    width, height = 800, 600
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # 1. Sky gradient
    for y in range(350):
        r = int(120 + (y / 350) * 80)
        g = int(180 + (y / 350) * 50)
        b = int(240 - (y / 350) * 30)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # 2. Celestial sphere (Sun)
    draw.ellipse([600, 80, 700, 180], fill=(255, 240, 160))

    # 3. Distant mountain peaks
    mountain_coords = [(0, 350), (150, 200), (320, 280), (500, 170), (680, 290), (800, 230), (800, 420), (0, 420)]
    draw.polygon(mountain_coords, fill=(80, 100, 130))

    # 4. Foreground rolling hills
    hill_coords = [(0, 380), (200, 330), (450, 370), (700, 320), (800, 360), (800, 600), (0, 600)]
    draw.polygon(hill_coords, fill=(45, 115, 65))

    # Foreground river
    river_coords = [(350, 420), (420, 420), (550, 600), (300, 600)]
    draw.polygon(river_coords, fill=(60, 130, 180))

    # Natural sensor grain simulation (deterministic Gaussian noise)
    np.random.seed(42)
    img_np = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, 3.5, img_np.shape)
    noisy_img = np.clip(img_np + noise, 0, 255).astype(np.uint8)
    final_img = Image.fromarray(noisy_img)

    # Build genuine EXIF tags for PIL
    exif = final_img.getexif()
    # 0x010F: Make, 0x0110: Model, 0x0132: DateTime
    exif[0x010F] = "Synthetic Specimen Lab (Test)"
    exif[0x0110] = "Simulated Optical Bench V1"
    exif[0x0132] = "2026:10:29 10:15:00"

    buffer = io.BytesIO()
    final_img.save(buffer, format="JPEG", quality=92, exif=exif)
    jpeg_bytes = buffer.getvalue()

    recipe = {
        "specimen_type": "camera_style",
        "description": "Synthetic natural landscape rendered with deterministic gradient shading and simulated Gaussian sensor noise.",
        "label": "Synthetic Demonstration Specimen — Not Real Case Evidence",
        "synthetic_exif": {
            "Make": "Synthetic Specimen Lab (Test)",
            "Model": "Simulated Optical Bench V1",
            "DateTime": "2026:10:29 10:15:00"
        }
    }
    return jpeg_bytes, "specimen_a_camera_photo.jpg", recipe


def generate_specimen_b_spliced_composite() -> tuple[bytes, str, dict]:
    """
    Specimen B: Spliced Composite (Synthetic Demonstration Specimen)
    Creates a base photographic background, recompressed at Q=75, then splices
    a high-contrast foreign badge object recompressed at Q=98, and injects
    an editing software tag ('GIMP 2.10 (Synthetic Demonstration)').
    """
    width, height = 800, 600
    
    # 1. Base image (architectural structure or urban scene)
    base = Image.new("RGB", (width, height), color=(210, 215, 225))
    draw = ImageDraw.Draw(base)
    # Background buildings
    draw.rectangle([50, 150, 220, 600], fill=(130, 140, 155))
    draw.rectangle([250, 100, 480, 600], fill=(110, 120, 135))
    draw.rectangle([520, 180, 750, 600], fill=(145, 155, 170))
    # Windows
    for r in range(120, 550, 40):
        for c in range(270, 460, 35):
            draw.rectangle([c, r, c + 20, r + 25], fill=(240, 245, 200))

    # Base was compressed at lower quality Q=75
    base_buf = io.BytesIO()
    base.save(base_buf, format="JPEG", quality=75)
    base_buf.seek(0)
    base_compressed = Image.open(base_buf).convert("RGB")

    # 2. Spliced foreign patch (uncompressed / Q=98 object inserted at center)
    patch_w, patch_h = 240, 160
    patch = Image.new("RGB", (patch_w, patch_h), color=(180, 40, 40))
    p_draw = ImageDraw.Draw(patch)
    p_draw.rectangle([10, 10, patch_w - 10, patch_h - 10], outline=(255, 215, 0), width=4)
    p_draw.ellipse([60, 30, patch_w - 60, patch_h - 30], fill=(220, 180, 50))
    
    # Paste spliced patch into base
    paste_x, paste_y = 280, 220
    composite = base_compressed.copy()
    composite.paste(patch, (paste_x, paste_y))

    # Add GIMP software trace in EXIF
    exif = composite.getexif()
    exif[0x0131] = "GIMP 2.10 (Synthetic Demonstration)"

    comp_buf = io.BytesIO()
    composite.save(comp_buf, format="JPEG", quality=90, exif=exif)
    composite_bytes = comp_buf.getvalue()

    recipe = {
        "specimen_type": "spliced_composite",
        "description": "Synthetic spliced composite containing inserted high-contrast badge spliced over Q=75 base image.",
        "label": "Synthetic Demonstration Specimen — Not Real Case Evidence",
        "ground_truth_bbox": [paste_x, paste_y, paste_x + patch_w, paste_y + patch_h],
        "software_signature": "GIMP 2.10 (Synthetic Demonstration)",
    }
    return composite_bytes, "specimen_b_spliced_composite.jpg", recipe


def generate_specimen_c_lossless_png() -> tuple[bytes, str, dict]:
    """
    Specimen C: Lossless PNG (Synthetic Demonstration Specimen)
    Creates a clean geometric calibration target in lossless PNG format.
    Demonstrates successful ingestion, hash, RGB analysis, and explicit JPEG ELA unavailability.
    """
    width, height = 600, 600
    img = Image.new("RGB", (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)

    # Calibration grid and concentric targets
    for i in range(50, 550, 50):
        draw.line([(i, 50), (i, 550)], fill=(200, 210, 225), width=1)
        draw.line([(50, i), (550, i)], fill=(200, 210, 225), width=1)

    # Concentric rings
    center_x, center_y = 300, 300
    colors_list = [(15, 30, 54), (197, 160, 89), (13, 148, 136), (217, 119, 6)]
    for idx, radius in enumerate(range(200, 20, -45)):
        col = colors_list[idx % len(colors_list)]
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            outline=col,
            width=3
        )

    # Center bullseye
    draw.ellipse([center_x - 15, center_y - 15, center_x + 15, center_y + 15], fill=(15, 30, 54))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()

    recipe = {
        "specimen_type": "lossless_png",
        "description": "Synthetic lossless calibration chart formatted as true 24-bit PNG.",
        "label": "Synthetic Demonstration Specimen — Not Real Case Evidence",
        "expected_behavior": "Ingests cleanly, computes SHA-256 and RGB statistics, reports JPEG ELA as unsupported format.",
    }
    return png_bytes, "specimen_c_lossless_chart.png", recipe
