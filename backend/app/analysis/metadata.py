import io
from pathlib import Path
from typing import Optional, Any
from PIL import Image, ExifTags
import exifread
from app.schemas.analysis import MetadataCategory, MetadataField

KNOWN_SOFTWARE_INDICATORS = [
    "photoshop", "adobe", "gimp", "lightroom", "canva", "pixlr",
    "snapseed", "paint.net", "corel", "affinity", "midjourney", "dall-e", "stable diffusion"
]

def _to_float(v: Any) -> float:
    """Helper to convert exifread Ratio, Pillow IFDRational, float, or int to float safely."""
    if hasattr(v, 'num') and hasattr(v, 'den'):
        return float(v.num) / float(v.den) if v.den != 0 else float(v.num)
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return float(v[0]) / float(v[1]) if v[1] != 0 else float(v[0])
    return float(v)

def format_gps_coord(coord_tags: Any, ref: str) -> Optional[str]:
    """Format GPS coordinates safely."""
    try:
        vals = coord_tags.values if hasattr(coord_tags, 'values') else coord_tags
        if vals and len(vals) >= 3:
            d = _to_float(vals[0])
            m = _to_float(vals[1])
            s = _to_float(vals[2])
            coord = d + (m / 60.0) + (s / 3600.0)
            if ref in ['S', 'W']:
                coord = -coord
            return f"{coord:.6f}° {ref}"
    except Exception:
        pass
    return None

def extract_image_metadata(file_bytes: bytes, filename: str) -> dict[str, Any]:
    """
    Forensic metadata inspection.
    Inspects EXIF / IPTC / TIFF metadata tags.
    Categorizes fields and marks statuses: Present, Missing, Unreadable, Unsupported.
    """
    categories: list[dict[str, Any]] = []
    summary_flags = {
        "has_exif": False,
        "software_trace_detected": False,
        "software_name": None,
        "has_gps": False,
        "gps_coords": None,
        "camera_make": None,
        "camera_model": None,
        "capture_timestamp": None,
    }

    # Use exifread for detailed parsing
    tags: dict[str, Any] = {}
    is_unreadable = False
    try:
        tags = exifread.process_file(io.BytesIO(file_bytes), details=True)
    except Exception:
        is_unreadable = True

    # Check Pillow EXIF as backup/complement
    pil_exif: dict[str, Any] = {}
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            raw_pil_exif = img.getexif()
            if raw_pil_exif:
                for k, v in raw_pil_exif.items():
                    name = ExifTags.TAGS.get(k, str(k))
                    pil_exif[name] = str(v)
    except Exception:
        pass

    if tags or pil_exif:
        summary_flags["has_exif"] = True

    # 1. Device & Camera Provenance
    make_val = str(tags.get("Image Make") or pil_exif.get("Make") or "")
    model_val = str(tags.get("Image Model") or pil_exif.get("Model") or "")
    
    camera_fields = [
        {
            "tag": "Make",
            "label": "Camera Manufacturer",
            "value": make_val if make_val else None,
            "status": "Present" if make_val else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Original hardware manufacturer tag." if make_val else "Not found in evidence bytes."
        },
        {
            "tag": "Model",
            "label": "Camera Hardware Model",
            "value": model_val if model_val else None,
            "status": "Present" if model_val else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Specific capture device designation." if model_val else "Not found in evidence bytes."
        }
    ]
    if make_val:
        summary_flags["camera_make"] = make_val
    if model_val:
        summary_flags["camera_model"] = model_val

    # 2. Timestamps & Chronology
    date_orig = str(tags.get("EXIF DateTimeOriginal") or pil_exif.get("DateTimeOriginal") or "")
    date_mod = str(tags.get("Image DateTime") or pil_exif.get("DateTime") or "")
    date_digitized = str(tags.get("EXIF DateTimeDigitized") or pil_exif.get("DateTimeDigitized") or "")

    time_fields = [
        {
            "tag": "DateTimeOriginal",
            "label": "Capture Timestamp (Original)",
            "value": date_orig if date_orig else None,
            "status": "Present" if date_orig else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Records the exact moment shutter was triggered." if date_orig else "Shutter timestamp not present."
        },
        {
            "tag": "DateTimeDigitized",
            "label": "Digitization Timestamp",
            "value": date_digitized if date_digitized else None,
            "status": "Present" if date_digitized else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Timestamp when analog sensor was converted to digital representation." if date_digitized else "Missing."
        },
        {
            "tag": "DateTime",
            "label": "Container Modification Timestamp",
            "value": date_mod if date_mod else None,
            "status": "Present" if date_mod else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Last file-container write time recorded by firmware or host." if date_mod else "Container timestamp missing."
        }
    ]
    if date_orig:
        summary_flags["capture_timestamp"] = date_orig

    # 3. Software & Processing Traces
    software_val = str(tags.get("Image Software") or pil_exif.get("Software") or "")
    artist_val = str(tags.get("Image Artist") or pil_exif.get("Artist") or "")
    
    is_sw_trace = False
    if software_val:
        low_sw = software_val.lower()
        if any(sw in low_sw for sw in KNOWN_SOFTWARE_INDICATORS):
            is_sw_trace = True
            summary_flags["software_trace_detected"] = True
            summary_flags["software_name"] = software_val

    software_fields = [
        {
            "tag": "Software",
            "label": "Processing Application / Firmware",
            "value": software_val if software_val else None,
            "status": "Present" if software_val else "Missing",
            "is_software_trace": is_sw_trace,
            "is_sensitive": False,
            "notes": "Identifies image editing suite or firmware encoder. Software traces indicate processing, not necessarily malicious manipulation." if software_val else "No software tag recorded in metadata."
        },
        {
            "tag": "Artist",
            "label": "Author / Creator Attribute",
            "value": artist_val if artist_val else None,
            "status": "Present" if artist_val else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "User or agency copyright/creator tag." if artist_val else "No author/artist tag present."
        }
    ]

    # 4. Exposure & Optical Parameters
    iso_val = str(tags.get("EXIF ISOSpeedRatings") or pil_exif.get("ISOSpeedRatings") or "")
    f_num = str(tags.get("EXIF FNumber") or pil_exif.get("FNumber") or "")
    exp_time = str(tags.get("EXIF ExposureTime") or pil_exif.get("ExposureTime") or "")
    focal_length = str(tags.get("EXIF FocalLength") or pil_exif.get("FocalLength") or "")

    optical_fields = [
        {
            "tag": "ISOSpeedRatings",
            "label": "Sensor Sensitivity (ISO)",
            "value": iso_val if iso_val else None,
            "status": "Present" if iso_val else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Sensor gain value at exposure." if iso_val else "Missing."
        },
        {
            "tag": "FNumber",
            "label": "Aperture (f-stop)",
            "value": f_num if f_num else None,
            "status": "Present" if f_num else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Lens diaphragm setting." if f_num else "Missing."
        },
        {
            "tag": "ExposureTime",
            "label": "Exposure Duration",
            "value": exp_time if exp_time else None,
            "status": "Present" if exp_time else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Shutter duration in seconds." if exp_time else "Missing."
        },
        {
            "tag": "FocalLength",
            "label": "Lens Focal Length",
            "value": focal_length if focal_length else None,
            "status": "Present" if focal_length else "Missing",
            "is_software_trace": False,
            "is_sensitive": False,
            "notes": "Focal length in millimeters." if focal_length else "Missing."
        }
    ]

    # 5. Geolocation (Sensitive!)
    gps_lat_tag = tags.get("GPS GPSLatitude")
    gps_lat_ref = str(tags.get("GPS GPSLatitudeRef") or "")
    gps_lon_tag = tags.get("GPS GPSLongitude")
    gps_lon_ref = str(tags.get("GPS GPSLongitudeRef") or "")
    
    formatted_lat = format_gps_coord(gps_lat_tag, gps_lat_ref)
    formatted_lon = format_gps_coord(gps_lon_tag, gps_lon_ref)
    has_gps = bool(formatted_lat and formatted_lon)
    if has_gps:
        summary_flags["has_gps"] = True
        summary_flags["gps_coords"] = f"{formatted_lat}, {formatted_lon}"

    gps_fields = [
        {
            "tag": "GPSCoordinates",
            "label": "Geographic Coordinates",
            "value": f"{formatted_lat}, {formatted_lon}" if has_gps else None,
            "status": "Present" if has_gps else "Missing",
            "is_software_trace": False,
            "is_sensitive": True,
            "notes": "CONFIDENTIAL: Geolocation metadata is sensitive personal data. Explicit confirmation required before exporting in external reports." if has_gps else "No geographic location recorded."
        }
    ]

    categories = [
        {"name": "Device & Hardware Provenance", "fields": camera_fields},
        {"name": "Chronological Timestamps", "fields": time_fields},
        {"name": "Software & Processing History", "fields": software_fields},
        {"name": "Optical & Exposure Parameters", "fields": optical_fields},
        {"name": "Geographic Location (Protected)", "fields": gps_fields},
    ]

    return {
        "categories": categories,
        "summary": summary_flags,
        "raw_tag_count": len(tags) + len(pil_exif),
        "is_unreadable": is_unreadable,
        "doctrine_note": "Metadata can be removed, altered, or forged. Absence of EXIF must not be interpreted as evidence of tampering."
    }
