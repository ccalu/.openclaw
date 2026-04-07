"""Load and validate S5 supervisor bootstrap."""
import sys
from pathlib import Path

from artifact_io import read_json
from schema_validator import validate_artifact_strict


REQUIRED_UPSTREAM_PATHS = [
    "source_package_path",
    "compiled_entities_path",
    "research_intake_path",
    "reference_ready_asset_pool_path",
    "video_context_path",
]


def load_bootstrap(path: Path) -> dict:
    """Read bootstrap JSON, validate schema, verify upstream paths exist."""
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(f"bootstrap not found: {path}")

    data = read_json(path)

    # Schema validation
    validate_artifact_strict(data, "supervisor_bootstrap")

    # Verify upstream paths exist on disk
    upstream = data.get("upstream", {})
    for key in REQUIRED_UPSTREAM_PATHS:
        p = upstream.get(key)
        if p and not Path(p).exists():
            raise FileNotFoundError(f"upstream {key} not found: {p}")

    return data


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: bootstrap_loader.py <bootstrap_path>")

    bootstrap_path = Path(sys.argv[1])
    data = load_bootstrap(bootstrap_path)
    print(f"OK: bootstrap loaded, job_id={data['job_id']}")
