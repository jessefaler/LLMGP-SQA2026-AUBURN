import json
import sys
import re

with open("requirements.json") as f:
    requirements = json.load(f)

with open("expected_structure.json") as f:
    expected_structure = json.load(f)

actual_ids = {r["requirement_id"] for r in requirements}
failures = []

# Every expected selected requirement should exist
for parent, suffixes in expected_structure.items():
    for s in suffixes:
        rid = f"{parent}{s}"
        if rid not in actual_ids:
            failures.append(f"Missing requirement: {rid}")

for rid in actual_ids:
    m = re.match(r"^(REQ-\d+\.\d+-\d+)([A-Z])", rid)
    if not m:
        continue
    parent = m.group(1)
    suffix = m.group(2)
    if parent in expected_structure and suffix not in expected_structure[parent]:
        # Only warn on top-level selected letters, not nested numeric ones like A1/B2
        if re.match(r"^REQ-\d+\.\d+-\d+[A-Z]$", rid):
            failures.append(f"Unexpected requirement: {rid}")

if failures:
    print("Validation FAILED:")
    for f in failures:
        print("-", f)
    sys.exit(1)
else:
    print("Validation passed: all selected expected requirements exist.")
    sys.exit(0)
