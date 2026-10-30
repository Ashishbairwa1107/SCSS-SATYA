import os
from pathlib import Path

# Resolve base project directory
# backend/app/core/config.py -> parents[3] is project root
CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parents[1]
BACKEND_DIR = CURRENT_FILE.parents[2]
PROJECT_ROOT = CURRENT_FILE.parents[3]

class Settings:
    PROJECT_NAME: str = "SCSS SATYA"
    PROJECT_FULL_TITLE: str = "SCSS SATYA — Forensic Image Authenticity Screening Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DOCTRINE: str = "The tool screens. The expert decides."
    ORGANIZATION: str = "Sure Clue Scientific Solutions (SCSS)"
    CHALLENGE: str = "SEVA FIRST Innovation Challenge 2026"
    SECTOR: str = "Sector 9 — Emerging Technologies (AI, Blockchain and Others)"
    SUB_THEME: str = "Sub-theme 4 — Responsible AI, Deepfake Detection, Cyber Resilience and Digital Trust"

    # Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Storage paths
    BASE_DIR: Path = PROJECT_ROOT
    PROJECT_ROOT: Path = PROJECT_ROOT
    STORAGE_DIR: Path = PROJECT_ROOT / "storage"
    VAULT_DIR: Path = STORAGE_DIR / "vault"
    ARTIFACTS_DIR: Path = STORAGE_DIR / "artifacts"
    REPORTS_DIR: Path = STORAGE_DIR / "reports"
    DB_DIR: Path = STORAGE_DIR / "database"

    @property
    def DATABASE_URL(self) -> str:
        db_file = (self.DB_DIR / "satya.db").resolve().as_posix()
        return f"sqlite:///{db_file}"

    # Frontend build directory for unified serving
    FRONTEND_DIST_DIR: Path = PROJECT_ROOT / "frontend" / "dist"

    # Ingestion constraints & security
    MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    MAX_IMAGE_PIXELS: int = 100_000_000  # 100 Megapixels
    MAX_IMAGE_DIMENSION: int = 16384     # Max width or height

    # Allowed extensions & MIME signatures
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp", ".bmp"}
    SUPPORTED_FORMATS: set = {"JPEG", "PNG", "TIFF", "WEBP", "BMP"}

    # Error Level Analysis parameters
    ELA_JPEG_QUALITY: int = 90
    ELA_AMPLIFICATION_SCALE: int = 15

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    CORS_ORIGIN_REGEX: str = r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$"

    def ensure_directories(self) -> None:
        self.VAULT_DIR.mkdir(parents=True, exist_ok=True)
        self.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.DB_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
