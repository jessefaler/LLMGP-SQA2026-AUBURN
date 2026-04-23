import json
import re
import sys

with open("requirements.json") as f:
    requirements = json.load(f)

with open("test_cases.json") as f:
    test_cases = json.load(f)

with open("expected_structure.json") as f:
    expected_structure = json.load(f)

# Build selected IDs from expected_structure.json
selected_ids = set()
for parent, suffixes in expected_structure.items():
    for s in suffixes:
        selected_ids.add(f"{parent}{s}")

# Test case requirement IDs
test_ids = {t.get("requirement_id", "") for t in test_cases}

failures = []
seen_ids = set()

for r in requirements:
    rid = r.get("requirement_id", "")

    for field in ["requirement_id", "description", "source"]:
        if field not in r:
            failures.append(f"Missing field '{field}' in requirement: {r}")

    # Accept IDs like REQ-117.130-001A or REQ-117.130-003B10
    if rid and not re.match(r"^REQ-\d+\.\d+-\d+[A-Z]\d*$", rid):
        failures.append(f"Invalid requirement_id format: {rid}")

    if rid in seen_ids:
        failures.append(f"Duplicate requirement_id: {rid}")
    seen_ids.add(rid)

    if "description" in r and "all hazards" in r["description"].lower():
        failures.append(f"Vague description in requirement: {rid}")

    if "parent" in r and rid and not rid.startswith(r["parent"]):
        failures.append(f"Parent-child ID mismatch: {rid} (parent {r['parent']})")

for rid in selected_ids:
    if rid not in test_ids:
        failures.append(f"No test case for selected requirement: {rid}")

# Check test case required fields
for t in test_cases:
    for field in ["test_case_id", "requirement_id", "description", "input_data", "expected_output"]:
        if field not in t:
            failures.append(f"Missing field '{field}' in test case: {t}")

if failures:
    print("Verification FAILED:")
    for f in failures:
        print("-", f)
    sys.exit(1)
else:
    print("Verification passed.")
    sys.exit(0)
