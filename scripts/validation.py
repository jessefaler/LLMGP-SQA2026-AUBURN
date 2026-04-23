import json
import sys
import re
from datetime import datetime


def log_event(event_type, status, details):
    record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "status": status,
        "details": details
    }
    with open("forensick_log.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")


# Load files
with open("requirements.json") as f:
    requirements = json.load(f)

with open("expected_structure.json") as f:
    expected_structure = json.load(f)

# Build actual IDs
actual_ids = {r["requirement_id"] for r in requirements if "requirement_id" in r}

failures = []

# Check all expected selected requirements exist
for parent, suffixes in expected_structure.items():
    for suffix in suffixes:
        rid = f"{parent}{suffix}"
        if rid not in actual_ids:
            failures.append(f"Missing requirement: {rid}")
            log_event(
                "missing_requirement",
                "fail",
                {"requirement_id": rid}
            )

# Optional: check for unexpected top-level requirements under tracked parents
for rid in actual_ids:
    match = re.match(r"^(REQ-\d+\.\d+-\d+)([A-Z])$", rid)
    if match:
        parent = match.group(1)
        suffix = match.group(2)

        if parent in expected_structure and suffix not in expected_structure[parent]:
            failures.append(f"Unexpected requirement: {rid}")
            log_event(
                "unexpected_requirement",
                "fail",
                {"requirement_id": rid}
            )

# Final result
if failures:
    log_event(
        "validation_complete",
        "fail",
        {"failure_count": len(failures)}
    )
    print("Validation FAILED:")
    for f in failures:
        print("-", f)
    sys.exit(1)
else:
    log_event(
        "validation_complete",
        "pass",
        {
            "tracked_parents": len(expected_structure),
            "actual_requirements": len(actual_ids)
        }
    )
    print("Validation passed: all selected expected requirements exist.")
    sys.exit(0)
