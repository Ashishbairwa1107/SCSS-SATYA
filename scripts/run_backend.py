import sys
import os
from pathlib import Path

# Resolve project root (parent of scripts/)
SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

# Ensure backend directory is in sys.path
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

def main():
    print("=" * 70)
    print(" SCSS SATYA — Forensic Image Authenticity Screening Platform")
    print(" Guiding Doctrine: 'The tool screens. The expert decides.'")
    print(" Sure Clue Scientific Solutions (SCSS)")
    print("=" * 70)

    try:
        from app.core.config import settings
        from app.database.session import engine, Base
        import app.database.models
        import uvicorn
    except ImportError as e:
        print(f"\n[FATAL STARTUP ERROR] Missing backend dependencies: {e}")
        print("Please activate your virtual environment and run:")
        print("    pip install -r backend/requirements.txt\n")
        sys.exit(1)

    # 1. Ensure required storage directories exist
    print("\n[1/4] Initializing storage directories...")
    settings.ensure_directories()
    print(f"      Vault:     {settings.VAULT_DIR}")
    print(f"      Artifacts: {settings.ARTIFACTS_DIR}")
    print(f"      Reports:   {settings.REPORTS_DIR}")
    print(f"      Database:  {settings.DB_DIR}")

    # 2. Initialize database tables
    print("[2/4] Verifying database schema...")
    Base.metadata.create_all(bind=engine)
    print("      Database initialized successfully.")

    # 3. Confirm frontend production build exists
    print("[3/4] Checking frontend production build...")
    dist_dir = settings.FRONTEND_DIST_DIR
    index_file = dist_dir / "index.html"
    if not index_file.exists():
        print(f"      [WARNING] Frontend production build not found at: {dist_dir}")
        print("      To build the production frontend, run:")
        print("          cd frontend && npm run build")
        print("      The backend API will still run, but SPA dashboard will not be served.")
    else:
        print(f"      Production frontend build verified at: {dist_dir}")

    # 4. Launch unified server
    print("[4/4] Starting Uvicorn ASGI server...")
    print("\n" + "-" * 70)
    print(" Platform endpoints:")
    print(f"   • Web Dashboard:     http://{settings.HOST}:{settings.PORT}/")
    print(f"   • API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f"   • ReDoc:             http://{settings.HOST}:{settings.PORT}/redoc")
    print(f"   • Health Check:      http://{settings.HOST}:{settings.PORT}/api/health")
    print("-" * 70 + "\n")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info",
    )

if __name__ == "__main__":
    main()
