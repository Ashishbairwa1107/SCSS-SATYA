# SCSS SATYA — Known Technical & Forensic Limitations

**Guiding Doctrine:** *"The tool screens. The expert decides."*

---

## 1. Digital Forensic & Scientific Boundaries

To maintain scientific credibility and prevent false claims in institutional settings, the limitations of SCSS SATYA are explicitly documented below.

### A. Absence of Detected Indicators $\neq$ Authenticity
The fact that an automated screening pipeline returns `No Indicator Detected` across all algorithmic checks **does not establish that the image is authentic, genuine, or unmanipulated**.
- Advanced digital manipulation (e.g., careful cloning along natural texture boundaries, localized color grading, or high-end manual retouching) can be executed without leaving macroscopic metadata or recompression signatures.
- Repeated global resaving or transmission over social media platforms can homogenize recompression error levels across the frame, concealing prior localized edits.

### B. Metadata is Neither Immutable nor Provenance Proof
- Container EXIF metadata is plaintext. Any hex editor or metadata utility (such as `exiftool`) can create, alter, or remove metadata fields in milliseconds.
- The presence of a camera make and model (e.g., `Nikon D850`) does not prove that the image was captured by that camera.
- Conversely, missing metadata is standard for images transmitted through messaging apps or exported from web browsers; it must never be construed as evidence of forgery.

### C. Error Level Analysis (ELA) Sensitivity
- ELA is not a universal deepfake or composite detector.
- ELA residual brightness depends heavily on spatial frequency, textural density, edge contrast, and color saturation. Natural high-contrast transitions (such as tree foliage against a bright sky or text lettering) naturally produce elevated error levels without any alteration.
- Applying JPEG ELA to lossless containers (PNG, TIFF) is scientifically invalid.

### D. Image Statistics are Non-Specific
- Global radiometric measurements (channel means, variance, histograms) and spatial noise metrics (Laplacian variance, noise residual sigma) reflect lighting, camera ISO sensitivity, optical depth-of-field, and scene composition.
- Low or high noise variance does not definitively indicate image manipulation or generative AI synthesis.

### E. Generative AI Detection Realities
- Pure rule-based screening tools cannot reliably detect pristine modern diffusion model outputs (e.g., Midjourney, DALL-E, Stable Diffusion) unless obvious geometric inconsistencies, lack of natural sensor PRNU, or generator-specific metadata tags are present.
- Never claim guaranteed deepfake or generative AI detection.

---

## 2. Integrity vs Authenticity Distinction

A matching SHA-256 cryptographic digest confirms that the stored byte sequence in the vault matches the exact bytes ingested at timestamp $T_0$.
- **What SHA-256 establishes:** The evidence file has not suffered bit rot, truncation, or disk tampering since it was registered into the platform.
- **What SHA-256 does NOT establish:** It provides no proof that the image was authentic or unaltered prior to ingestion. A deepfake hashed upon upload will verify with a 100% matching hash.

---

## 3. Statutory and Judicial Disclaimers (India & Global)

### A. ISO/IEC 17025 Laboratory Accreditation
SCSS SATYA is a research, demonstration, and screening prototype developed for the SEVA FIRST Innovation Challenge 2026. **It is not certified or accredited under ISO/IEC 17025:2017** as a certified forensic testing laboratory instrument.

### B. Section 63 Bharatiya Sakshya Adhiniyam, 2023 (BSA)
In Indian courts, electronic records are governed by **Section 63 of the Bharatiya Sakshya Adhiniyam, 2023 (BSA)** (which supersedes the historical Section 65B framework of the Indian Evidence Act, 1872).
- Section 63 requires a formal certificate signed by the person in lawful control or management of the device, or an authorized expert.
- Automated software reports produced by this application constitute technical screening aids. They do **not** automatically satisfy statutory Section 63 requirements without independent expert verification and formal legal certification.

### C. Local Database Audit Trail
The audit trail is stored locally in SQLite (`satya.db`). While protected against inadvertent application-level modification, a local SQLite database is **not an independently immutable or distributed ledger (blockchain)**. A user with direct administrative filesystem access can alter the SQLite database.
