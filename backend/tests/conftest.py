import io
import sys
from pathlib import Path
import pytest

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.session import Base, get_db
from app.core.config import settings

# Test database
TEST_DB_PATH = (settings.DB_DIR / "test_satya.db").resolve()
test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH.as_posix()}",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    settings.ensure_directories()
    Base.metadata.create_all(bind=test_engine)
    yield
    # Teardown
    Base.metadata.drop_all(bind=test_engine)
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass

@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_jpeg_bytes():
    """Create a minimal valid test JPEG with distinct red/blue regions."""
    img = Image.new("RGB", (200, 150), color=(200, 50, 50))
    for x in range(50, 150):
        for y in range(30, 100):
            img.putpixel((x, y), (50, 50, 220))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

@pytest.fixture
def sample_png_bytes():
    """Create a minimal valid test PNG."""
    img = Image.new("RGB", (100, 100), color=(30, 150, 90))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
