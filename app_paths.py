from pathlib import Path
import sys

# Packaged application lives in Edit/.app/CutReview; recordings and choices stay in Edit.
ROOT = Path(sys.executable).resolve().parents[2] if getattr(sys,'frozen',False) else Path(__file__).resolve().parent

def add_dependencies():
    location=str(ROOT/'.runtime-deps')
    if getattr(sys,'frozen',False):
        # Prefer the application's bundled Qt libraries over loose analysis packages.
        sys.path.append(location)
    else:
        sys.path.insert(0,location)
