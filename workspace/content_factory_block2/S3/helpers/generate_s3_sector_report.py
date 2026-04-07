import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: generate_s3_sector_report.py <compiled_entities_path> <report_path>")

    compiled_path = Path(sys.argv[1])
    report_path = Path(sys.argv[2])

    compiled = json.loads(compiled_path.read_text(encoding="utf-8"))
    ce = compiled.get("compiled_entities", {})
    ops = compiled.get("operators", {})

    lines = [
        "# S3 Sector Report",
        "",
        "## Job",
        f"- job_id: {compiled.get('job_id')}",
        f"- video_id: {compiled.get('video_id')}",
        f"- account_id: {compiled.get('account_id')}",
        f"- language: {compiled.get('language')}",
        "",
        "## Final Status",
        f"- status: {compiled.get('status')}",
        f"- generated_at: {utc_now()}",
        "",
        "## Operators",
    ]

    for op_name, info in ops.items():
        lines.append(f"- {op_name}: {info.get('status')}")

    lines += [
        "",
        "## Entity Summary",
        f"- human_subjects: {len(ce.get('human_subjects', []))}",
        f"- environment_locations: {len(ce.get('environment_locations', []))}",
        f"- object_artifacts: {len(ce.get('object_artifacts', []))}",
        f"- symbolic_events: {len(ce.get('symbolic_events', []))}",
        "",
        "## Warnings",
    ]

    warnings = compiled.get("warnings", [])
    if warnings:
        lines.extend([f"- {w}" for w in warnings])
    else:
        lines.append("- none")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(report_path))


if __name__ == "__main__":
    main()
