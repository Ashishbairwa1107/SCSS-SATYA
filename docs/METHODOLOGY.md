# SCSS SATYA — Scientific & Forensic Methodology

**Full Project Title:** SCSS SATYA — Forensic Image Authenticity Screening Platform  
**Guiding Doctrine:** *"The tool screens. The expert decides."*

---

## 1. Overview of Forensic Image Screening

Digital image forensics operates under the reality that no single automated algorithmic signal definitively proves that a digital photograph is genuine or forged. Real-world images undergo routine processing (cropping, resizing, color calibration, format conversion, and social media re-compression) that modifies file bytes and metadata without malicious intent.

SCSS SATYA provides an institutional-grade screening methodology that extracts objective, reproducible measurements, preserves evidence integrity, and presents explainable technical indicators to assist authorized forensic experts.

---

## 2. Ingestion & Cryptographic Integrity (Layer 1 & Layer 2)

### A. Raw Ingestion & Hashing
1. **Pristine Byte Capture:** The uploaded byte array is hashed immediately upon receipt using Python `hashlib.sha256()`.
2. **Hash Isolation:** The hash is computed strictly from the raw network byte stream—never from resized bitmaps, decoded NumPy arrays, or browser previews.
3. **Non-Overwriting Storage:** Stored in `storage/vault/` with a generated name `evd_{uuid4}_{hash_prefix}.{ext}`.
4. **Integrity Re-Verification:**
   $$\text{Verification Result} = \begin{cases} \text{VERIFIED}, & \text{if } H(\text{stored\_bytes}) == H_{\text{ingest}} \\ \text{MISMATCH}, & \text{otherwise} \end{cases}$$
   If a single bit is modified, the re-computed hash diverges, instantly flagging an integrity failure.

### B. Input Validation & DoS Mitigation
- **Size Limit:** Max 50 MB byte payload.
- **Decompression Bomb Defense:** Maximum image dimensions capped at 16,384 px; maximum pixel census capped at $100 \times 10^6$ pixels ($100\text{ MP}$).
- **Magic Byte Verification:** File extensions are cross-checked with decoded image headers using Pillow `Image.verify()`.

---

## 3. Metadata Inspection Protocol

Metadata is extracted using both `exifread` and Pillow `getexif()`. Fields are classified into four explicit evidentiary statuses:
- **Present:** Tag exists, was parsed cleanly, and contains a decoded value.
- **Missing:** Tag is absent in the evidence container.
- **Unreadable:** Tag data exists but is corrupted, unparseable, or contains non-standard binary structure.
- **Unsupported:** Container format does not define or accommodate the metadata field.

### Key Inspection Fields
- **Device Provenance:** `Make`, `Model` (indicates camera hardware manufacturer and model designation).
- **Chronology:** `DateTimeOriginal` (shutter trigger timestamp), `DateTimeDigitized` (sensor ADC conversion), `DateTime` (container file modification).
- **Software Traces:** Scanned for known graphics suites (`Photoshop`, `GIMP`, `Lightroom`, `Canva`, etc.). Observed software traces are documented as technical observations, not definitive proof of manipulation.
- **Geolocation:** `GPSLatitude`, `GPSLongitude`. Masked in the UI by default to protect privacy, with explicit disclosure required before export.

> **Forensic Rule on Missing Metadata:**  
> Messaging services (WhatsApp, Telegram, Signal) and social media platforms (Facebook, Instagram, X) routinely strip metadata for bandwidth optimization and user privacy. Missing EXIF metadata must never be interpreted as evidence of malicious tampering.

---

## 4. Error Level Analysis (ELA)

### A. Mathematical Principle
JPEG compression divides an image into $8 \times 8$ pixel blocks, transforms them using the Discrete Cosine Transform (DCT), and quantizes high-frequency coefficients according to a quantization table. When an image is resaved at a known quality setting ($Q$), the error between successive lossy compression cycles diminishes until equilibrium is reached:

$$\Delta(x, y) = | I_{\text{original}}(x, y) - I_{\text{recompressed}}(x, y, Q=90) |$$

$$\text{ELA}_{\text{amplified}}(x, y) = \min(255, \Delta(x, y) \times 15)$$

### B. Thermal Heatmap Representation
In addition to grayscale amplification, SCSS SATYA applies the OpenCV `COLORMAP_INFERNO` thermal transfer function. Darker hues (black, purple) indicate minimal recompression error; bright hues (yellow, white) indicate high recompression error.

### C. Scientific Boundaries & Lossless Inapplicability
- High-contrast natural boundaries, saturated primary colors, fine textures, and text overlays naturally produce higher ELA residuals without any tampering.
- Splicing an uncompressed or high-quality element into a heavily compressed background often results in divergent residual intensity.
- **Lossless Formats (PNG, TIFF, BMP):** Lossless formats do not use lossy DCT quantization tables. Applying JPEG ELA to PNG produces invalid or synthetic artifacts. SATYA explicitly rejects ELA for non-JPEG formats and reports `Inconclusive (Format Unsupported)`.

---

## 5. Image Geometry & Spatial Noise Metrics

### A. Radiometric RGB Statistics
A full-frame 100% pixel census calculates per-channel mean ($\mu$), standard deviation ($\sigma$), minimum, maximum, and median values. A 32-bin histogram (bin width 8) models color channel dynamic range and clipping.

### B. Spatial Sharpness (Laplacian Variance)
$$\text{Var}(\nabla^2 I) = \frac{1}{N} \sum_{x, y} \left( L(x, y) - \mu_L \right)^2$$
Where $L = \text{Laplacian}(I_{\text{gray}})$. Low values indicate global blur, heavy denoising, or flat vector synthesis; high values reflect sharp edges or optical grain.

### C. High-Frequency Noise Residual ($\sigma_{\text{noise}}$)
High-frequency spatial noise is estimated by measuring the residual difference between the grayscale image and a $3 \times 3$ median-filtered counterpart:
$$\sigma_{\text{noise}} \approx 1.4826 \times \text{Mean}(| I_{\text{gray}} - \text{MedianFilter}(I_{\text{gray}}) |)$$

---

## 6. Explainable Technical Findings Engine

To eliminate arbitrary black-box claims, every finding uses one of three statuses:
1. **No Indicator Detected:** Measurement falls within expected nominal baselines for the given format.
2. **Indicator Observed:** Empirical anomaly, editing software signature, or residual divergence detected.
3. **Inconclusive:** Absence of metadata or format limitations prevent automated evaluation.

Every finding includes:
- **Observed Measurement:** Empirical numeric or string evidence.
- **Technical Explanation:** How the measurement was acquired.
- **Forensic Significance:** Potential implications for authenticity.
- **Known Limitations:** Alternative legitimate explanations for the observation.
- **Recommended Action:** Specific verification step for the qualified human examiner.
