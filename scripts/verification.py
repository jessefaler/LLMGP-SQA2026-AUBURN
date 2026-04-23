import json
import re
import sys
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

with open("test_cases.json") as f:
    test_cases = json.load(f)

with open("expected_structure.json") as f:
    expected_structure = json.load(f)

# Build selected requirement IDs from expected_structure.json
selected_ids = set()
for parent, suffixes in expected_structure.items():
    for suffix in suffixes:
        selected_ids.add(f"{parent}{suffix}")

# Collect requirement IDs referenced by test cases
test_ids = {t.get("requirement_id", "") for t in test_cases}

failures = []
seen_ids = set()

for r in requirements:
    rid = r.get("requirement_id", "")

    # Rule 1: Required fields
    for field in ["requirement_id", "description", "source"]:
        if field not in r:
            failures.append(f"Missing field '{field}' in requirement: {r}")
            log_event(
                "missing_requirement_field",
                "fail",
                {"requirement_id": rid, "missing_field": field}
            )

    # Rule 2: ID format
    # Accept IDs like:
    # REQ-117.130-001A
    # REQ-117.130-003B10
    if rid and not re.match(r"^REQ-\d+\.\d+-\d+[A-Z]\d*$", rid):
        failures.append(f"Invalid requirement_id format: {rid}")
        log_event(
            "invalid_requirement_id_format",
            "fail",
            {"requirement_id": rid}
        )

    # Rule 3: Duplicate requirement IDs
    if rid:
        if rid in seen_ids:
            failures.append(f"Duplicate requirement_id: {rid}")
            log_event(
                "duplicate_requirement_id",
                "fail",
                {"requirement_id": rid}
            )
        seen_ids.add(rid)

    # Rule 4: No vague phrase
    if "description" in r and "all hazards" in r["description"].lower():
        failures.append(f"Vague description in requirement: {rid}")
        log_event(
            "vague_requirement_description",
            "fail",
            {"requirement_id": rid}
        )

    # Rule 5: Parent-child consistency
    if "parent" in r and rid and not rid.startswith(r["parent"]):
        failures.append(f"Parent-child ID mismatch: {rid} (parent {r['parent']})")
        log_event(
            "parent_child_mismatch",
            "fail",
            {"requirement_id": rid, "parent": r["parent"]}
        )

# Rule 6: Only selected requirements must have test cases
for rid in selected_ids:
    if rid not in test_ids:
        failures.append(f"No test case for selected requirement: {rid}")
        log_event(
            "missing_test_case",
            "fail",
            {"requirement_id": rid}
        )

# Rule 7: Required test case fields
for t in test_cases:
    tcid = t.get("test_case_id", "")
    for field in ["test_case_id", "requirement_id", "description", "input_data", "expected_output"]:
        if field not in t:
            failures.append(f"Missing field '{field}' in test case: {t}")
            log_event(
                "missing_test_case_field",
                "fail",
                {"test_case_id": tcid, "missing_field": field}
            )

# Final result
if failures:
    log_event(
        "verification_complete",
        "fail",
        {"failure_count": len(failures)}
    )
    print("Verification FAILED:")
    for f in failures:
        print("-", f)
    sys.exit(1)
else:
    log_event(
        "verification_complete",
        "pass",
        {
            "checked_requirements": len(requirements),
            "checked_test_cases": len(test_cases),
            "selected_requirements": len(selected_ids)
        }
    )
    print("Verification passed.")
    sys.exit(0)
