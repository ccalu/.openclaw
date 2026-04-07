"""Load and validate S4 supervisor bootstrap."""
import sys
from pathlib import Path

from artifact_io import read_json
from schema_validator import validate_artifact_strict


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
    compiled_path = upstream.get("compiled_entities_path")
    if compiled_path and not Path(compiled_path).exists():
        raise FileNotFoundError(f"upstream compiled_entities_path not found: {compiled_path}")

    sector_report = upstream.get("sector_report_path")
    if sector_report and not Path(sector_report).exists():
        raise FileNotFoundError(f"upstream sector_report_path not found: {sector_report}")

    return data


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: bootstrap_loader.py <bootstrap_path>")

    bootstrap_path = Path(sys.argv[1])
    data = load_bootstrap(bootstrap_path)
    print(f"OK: bootstrap loaded, job_id={data['job_id']}")
