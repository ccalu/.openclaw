"""S5 directory creation."""
import sys
from pathlib import Path


SECTOR_DIRS = [
    "intake",
    "scene_direction_input_packages",
    "scene_kit_specs",
    "compiled",
    "runtime",
    "checkpoints",
    "logs",
]


def create_s5_directories(sector_root: Path) -> None:
    """Create all S5 sector-level directories (idempotent)."""
    sr = sector_root.resolve()
    for d in SECTOR_DIRS:
        (sr / d).mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: dirs.py <sector_root>")
    sr = Path(sys.argv[1]).resolve()
    create_s5_directories(sr)
    print(str(sr))
