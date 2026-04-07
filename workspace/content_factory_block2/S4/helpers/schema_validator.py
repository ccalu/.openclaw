"""JSON Schema validation against S4 schemas."""
import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator

SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


def load_schema(name: str) -> dict:
    """Load a schema by name (e.g. 'supervisor_bootstrap' -> supervisor_bootstrap.schema.json)."""
    schema_file = SCHEMAS_DIR / f"{name}.schema.json"
    if not schema_file.exists():
        raise FileNotFoundError(f"schema not found: {schema_file}")
    return json.loads(schema_file.read_text(encoding="utf-8"))


def validate_artifact(data: dict, schema_name: str) -> tuple:
    """Validate data against schema. Returns (is_valid, errors_list)."""
    schema = load_schema(schema_name)
    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(data))
    if not errors:
        return True, []
    return False, [f"{e.json_path}: {e.message}" for e in errors]


def validate_artifact_strict(data: dict, schema_name: str) -> None:
    """Validate data against schema. Raises on first error."""
    valid, errors = validate_artifact(data, schema_name)
    if not valid:
        raise ValueError(f"schema validation failed ({schema_name}): {errors[0]}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: schema_validator.py <artifact_path> <schema_name>")

    artifact_path = Path(sys.argv[1])
    schema_name = sys.argv[2]

    data = json.loads(artifact_path.read_text(encoding="utf-8"))
    valid, errors = validate_artifact(data, schema_name)

    if valid:
        print(f"VALID: {artifact_path} passes {schema_name}")
    else:
        print(f"INVALID: {artifact_path} fails {schema_name}")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
