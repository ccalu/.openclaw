import json
import sys
from pathlib import Path


def fail(message: str, code: int = 1):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    sys.exit(code)


def main():
    if len(sys.argv) != 4:
        fail("usage: validate_operator_output.py <operator_name> <output_path> <schema_path>")

    operator_name = sys.argv[1]
    output_path = Path(sys.argv[2])
    schema_path = Path(sys.argv[3])

    if not output_path.exists():
        fail(f"output file not found: {output_path}")
    if not schema_path.exists():
        fail(f"schema file not found: {schema_path}")

    try:
        data = json.loads(output_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid json output: {exc}")

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid json schema file: {exc}")

    required = schema.get("required", [])
    missing = [key for key in required if key not in data]
    if missing:
        fail(f"missing required fields: {missing}")

    actual_operator = data.get("operator_name")
    if actual_operator != operator_name:
        fail(f"operator_name mismatch: expected {operator_name}, got {actual_operator}")

    entities = data.get("entities")
    if not isinstance(entities, list):
        fail("entities must be a list")

    status = data.get("status")
    if status not in {"completed", "failed"}:
        fail("status must be completed or failed")

    print(json.dumps({
        "ok": True,
        "operator_name": operator_name,
        "output_path": str(output_path),
        "entity_count": len(entities),
        "status": status,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
