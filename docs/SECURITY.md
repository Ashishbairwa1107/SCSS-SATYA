# SCSS SATYA — Security Model & Threat Assessment

**Developed for:** Sure Clue Scientific Solutions (SCSS)  
**Challenge:** SEVA FIRST Innovation Challenge 2026

---

## 1. Threat Model & Trust Assumptions

In a digital forensic laboratory, incoming files must be treated as **untrusted, potentially adversarial evidence specimens**. Potential threats include:
1. **Malicious Payloads:** Embedding executable scripts, polyglots, or exploits within image containers.
2. **Decompression Bombs (Zip/Pixel Bombs):** Specially crafted files with small compressed sizes that expand into gigabytes in memory to exhaust system RAM.
3. **Directory Traversal Attacks:** Supplying manipulated filenames (e.g., `../../etc/passwd` or `..\Windows\System32\cmd.exe`) to access or overwrite host files.
4. **Evidence Tampering:** Modification of stored evidence bytes after ingestion to alter legal findings.
5. **Information Leakage:** Exposing absolute server paths, database credentials, or sensitive personal data (e.g., GPS coordinates).

---

## 2. Implemented Security Controls

### A. Input Sanitization & Path Traversal Elimination
- Filenames provided by users are completely sanitized using `re.sub(r'[^a-zA-Z0-9_\-\.]', '_', ...)`.
- All storage operations enforce strict root boundary checks via `validate_safe_path()`:
  ```python
  def validate_safe_path(target_path: Path, allowed_root: Path) -> Path:
      resolved_target = target_path.resolve()
      resolved_root = allowed_root.resolve()
      resolved_target.relative_to(resolved_root)  # Raises ValueError if outside
      return resolved_target
  ```
- Storage files in `storage/vault/`, `storage/artifacts/`, and `storage/reports/` use non-overwriting randomized UUID filenames (`evd_{uuid4}_{hash_prefix}.{ext}`).

### B. Safe Image Decoding & Decompression Bomb Protection
- `Image.MAX_IMAGE_PIXELS = 100_000_000` is enforced on all Pillow decoding operations.
- Images exceeding 16,384 px in width or height are rejected prior to full decoding.
- `Image.verify()` validates container integrity before processing pixel buffers.

### C. Evidence Hash Immutability
- SHA-256 digests are computed directly from pristine incoming bytes before any downstream transformations.
- Stored bytes are preserved read-only in the vault. The platform provides no endpoint or function that modifies original evidence files.

### D. Sensitive Data & Privacy Protection
- Geolocation metadata (`GPSLatitude`, `GPSLongitude`) is classified as sensitive personal data. It is masked by default in the UI and requires explicit operator authorization before being revealed or included in exported forensic reports.

### E. Error Masking & Sanitization
- Global exception handlers sanitize server stack traces, masking absolute workspace directories with `[STORAGE_ROOT]`.
- Database queries use parameterized SQLAlchemy ORM statements, eliminating SQL injection vectors.

---

## 3. Deployment Constraints & Production Requirements

> **PROTOTYPE DEPLOYMENT NOTICE:**  
> This initial implementation is engineered for a **trusted local workstation environment**. It does not include multi-tenant user authentication (RBAC) or cryptographic hardware security modules (HSM).

Before deploying SCSS SATYA to an institutional multi-user network or internet-facing forensic infrastructure, the following measures must be implemented:
1. **Authentication & Authorization:** Integration with institutional SSO (OAuth2 / OIDC / SAML) and strict Role-Based Access Control (RBAC) separating Case Investigators, Forensic Examiners, and Laboratory Supervisors.
2. **Encrypted Storage at Rest:** Encrypting the `storage/vault/` directory using AES-256 or hardware-encrypted storage media (FIPS 140-2 Level 3).
3. **Transport Security:** Mandatory TLS 1.3 encryption across all network communication.
4. **Append-Only Write Once Read Many (WORM) Storage:** Storing evidence on hardware WORM drives or cryptographically signed append-only ledgers to prevent even privileged administrator tampering.
