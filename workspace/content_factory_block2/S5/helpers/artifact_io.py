"""Artifact IO. JSON + markdown read/write with encoding safety."""
import json
from datetime import datetime, timezone
from pathlib import Path


def write_json(path: Path, data: dict) -> None:
    """Write dict as JSON. Creates parent dirs as needed."""
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    """Read JSON file and return dict."""
    return json.loads(path.resolve().read_text(encoding="utf-8"))


def write_markdown(path: Path, content: str) -> None:
    """Write markdown content. Creates parent dirs as needed."""
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def artifact_exists(path: Path) -> bool:
    """Check if artifact file exists on disk."""
    return path.resolve().exists()


def utc_now() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()
