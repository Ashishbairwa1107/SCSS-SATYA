import io
from typing import Any
from PIL import Image
import numpy as np
import cv2

def calculate_image_statistics(file_bytes: bytes) -> dict[str, Any]:
    """
    Perform reproducible spatial geometry, color channel distribution,
    and high-frequency spatial noise measurements.
    """
    with Image.open(io.BytesIO(file_bytes)) as img:
        width, height = img.size
        mode = img.mode
        rgb_img = img.convert("RGB")
        img_np = np.array(rgb_img)

    aspect_ratio = round(width / max(height, 1), 4)
    total_pixels = width * height

    # Color channel separation
    r_channel = img_np[:, :, 0]
    g_channel = img_np[:, :, 1]
    b_channel = img_np[:, :, 2]

    # Calculate statistics per channel
    def channel_stats(ch: np.ndarray) -> dict[str, float]:
        return {
            "mean": round(float(np.mean(ch)), 2),
            "std_dev": round(float(np.std(ch)), 2),
            "min": float(np.min(ch)),
            "max": float(np.max(ch)),
            "median": float(np.median(ch)),
        }

    r_stat = channel_stats(r_channel)
    g_stat = channel_stats(g_channel)
    b_stat = channel_stats(b_channel)

    # Compute 32-bin histograms for Recharts frontend visualization
    # 256 intensity levels -> 32 bins of width 8
    bins = 32
    bin_range = (0, 256)
    r_hist, _ = np.histogram(r_channel, bins=bins, range=bin_range)
    g_hist, _ = np.histogram(g_channel, bins=bins, range=bin_range)
    b_hist, _ = np.histogram(b_channel, bins=bins, range=bin_range)

    histogram_data = []
    for i in range(bins):
        start_val = i * 8
        end_val = (i + 1) * 8 - 1
        histogram_data.append({
            "bin": i,
            "range": f"{start_val}-{end_val}",
            "r": int(r_hist[i]),
            "g": int(g_hist[i]),
            "b": int(b_hist[i]),
        })

    # Spatial noise & gradient analysis using OpenCV
    gray_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    # 1. Laplacian variance (standard high-frequency edge & spatial sharpness measurement)
    laplacian = cv2.Laplacian(gray_np, cv2.CV_64F)
    laplacian_var = round(float(laplacian.var()), 2)

    # 2. Sobel gradient mean (spatial intensity gradient magnitude)
    sobel_x = cv2.Sobel(gray_np, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray_np, cv2.CV_64F, 0, 1, ksize=3)
    gradient_mag = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel_mean = round(float(np.mean(gradient_mag)), 2)

    # 3. High-frequency noise estimation via median filter residual
    # Residual = |image - median_filtered|
    med_filtered = cv2.medianBlur(gray_np, 3)
    noise_residual = np.abs(gray_np.astype(np.float32) - med_filtered.astype(np.float32))
    noise_sigma = round(float(np.mean(noise_residual) * 1.4826), 2)  # MAD estimator approximation

    return {
        "geometry": {
            "width": width,
            "height": height,
            "aspect_ratio": aspect_ratio,
            "total_pixels": total_pixels,
            "color_mode": mode,
        },
        "rgb_statistics": {
            "red": r_stat,
            "green": g_stat,
            "blue": b_stat,
            "histogram": histogram_data,
            "total_pixels_sampled": total_pixels,
            "sampling_method": "Full-frame deterministic pixel census (100% pixel sample)",
            "interpretation": (
                f"Full-frame color distribution: Red mean={r_stat['mean']}, Green mean={g_stat['mean']}, Blue mean={b_stat['mean']}. "
                "Channel variance reflects scene illumination, white balance, and chromatic tonality."
            )
        },
        "spatial_noise": {
            "laplacian_variance": laplacian_var,
            "sobel_gradient_mean": sobel_mean,
            "high_freq_noise_sigma": noise_sigma,
            "method_name": "Laplacian variance & median-filter high-frequency residual estimator",
            "interpretation": (
                f"Measured Laplacian variance is {laplacian_var:.1f} and high-frequency noise sigma is {noise_sigma:.2f}. "
                "These values reflect overall sharpness, edge density, and spatial grain texture across the frame."
            ),
            "limitations": (
                "Sensor ISO settings, optical depth of field, atmospheric haze, lighting, and JPEG compression "
                "directly influence noise and sharpness measurements. High or low variance alone does not prove tampering."
            )
        }
    }
