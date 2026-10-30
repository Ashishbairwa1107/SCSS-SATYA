import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPTS_DIR.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.services.specimens import (
    generate_specimen_a_camera_photo,
    generate_specimen_b_spliced_composite,
    generate_specimen_c_lossless_png,
)

def main():
    print("Generating calibrated forensic demonstration specimens...")
    target_dir = settings.STORAGE_DIR / "specimens"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Specimen A
    bytes_a, name_a, recipe_a = generate_specimen_a_camera_photo()
    path_a = target_dir / name_a
    with open(path_a, "wb") as f:
        f.write(bytes_a)
    print(f"  [+] Specimen A written: {path_a} ({len(bytes_a):,} bytes)")

    # Specimen B
    bytes_b, name_b, recipe_b = generate_specimen_b_spliced_composite()
    path_b = target_dir / name_b
    with open(path_b, "wb") as f:
        f.write(bytes_b)
    print(f"  [+] Specimen B written: {path_b} ({len(bytes_b):,} bytes)")

    # Specimen C
    bytes_c, name_c, recipe_c = generate_specimen_c_lossless_png()
    path_c = target_dir / name_c
    with open(path_c, "wb") as f:
        f.write(bytes_c)
    print(f"  [+] Specimen C written: {path_c} ({len(bytes_c):,} bytes)")

    print("\nAll demonstration specimens generated successfully in storage/specimens/.")

if __name__ == "__main__":
    main()
