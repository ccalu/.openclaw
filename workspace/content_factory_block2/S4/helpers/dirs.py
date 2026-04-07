"""S4 directory creation."""
import sys
from pathlib import Path


SECTOR_DIRS = [
    "intake",
    "batches",
    "targets",
    "compiled",
    "runtime",
    "dispatch",
    "logs",
]

TARGET_DIRS = [
    "assets",
    "candidates",
    "previews",
    "captures",
]


def create_s4_directories(sector_root: Path) -> None:
    """Create all S4 sector-level directories."""
    sr = sector_root.resolve()
    for d in SECTOR_DIRS:
        (sr / d).mkdir(parents=True, exist_ok=True)


def create_target_directories(target_root: Path) -> None:
    """Create all per-target subdirectories."""
    tr = target_root.resolve()
    tr.mkdir(parents=True, exist_ok=True)
    for d in TARGET_DIRS:
        (tr / d).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: dirs.py <sector_root>")
    sr = Path(sys.argv[1]).resolve()
    create_s4_directories(sr)
    print(str(sr))
