from app.analysis.ela import perform_error_level_analysis
from app.analysis.image_statistics import calculate_image_statistics
from app.analysis.metadata import extract_image_metadata
from app.services.specimens import generate_specimen_a_camera_photo, generate_specimen_c_lossless_png

def test_exif_metadata_extraction():
    """Test 12 & 13: Metadata extraction and honest missing metadata classification."""
    # Specimen A contains genuine embedded EXIF tags
    photo_bytes, _, _ = generate_specimen_a_camera_photo()
    meta = extract_image_metadata(photo_bytes, "photo.jpg")
    assert meta["summary"]["has_exif"] is True
    assert "Synthetic Specimen Lab (Test)" in meta["summary"]["camera_make"]

    # Image without EXIF
    empty_bytes, _, _ = generate_specimen_c_lossless_png()
    meta_empty = extract_image_metadata(empty_bytes, "chart.png")
    # Missing EXIF must include doctrine note that absence does not indicate tampering
    assert "Absence of EXIF must not be interpreted as evidence of tampering" in meta_empty["doctrine_note"]

def test_jpeg_error_level_analysis(sample_jpeg_bytes):
    """Test 14: JPEG ELA computes residual difference and creates artifact."""
    ela = perform_error_level_analysis(sample_jpeg_bytes, detected_format="JPEG", quality=90, scale=15)
    assert ela["format_supported"] is True
    assert ela["quality"] == 90
    assert ela["scale"] == 15
    assert ela["artifact_id"] is not None
    assert ela["mean_difference"] is not None
    assert ela["residual_std"] is not None
    assert "ELA is not a universal" in ela["limitation_statement"]

def test_png_ela_rejection_and_explanation(sample_png_bytes):
    """Test 15: Lossless PNG ELA refusal with transparent explanation."""
    ela = perform_error_level_analysis(sample_png_bytes, detected_format="PNG")
    assert ela["format_supported"] is False
    assert ela["artifact_id"] is None
    assert "JPEG-specific" in ela["notes"]
    assert "lossless formats" in ela["limitation_statement"]

def test_rgb_and_spatial_noise_statistics(sample_jpeg_bytes):
    """Test 16: RGB channel statistics and spatial noise metrics calculation."""
    stats = calculate_image_statistics(sample_jpeg_bytes)
    assert "geometry" in stats
    assert stats["geometry"]["width"] == 200
    assert stats["geometry"]["height"] == 150

    rgb = stats["rgb_statistics"]
    assert "red" in rgb and "green" in rgb and "blue" in rgb
    assert rgb["red"]["mean"] > 0
    assert len(rgb["histogram"]) == 32

    spatial = stats["spatial_noise"]
    assert spatial["laplacian_variance"] >= 0
    assert spatial["high_freq_noise_sigma"] >= 0
    assert "limitations" in spatial
