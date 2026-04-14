# scripts/generate_requirements.py
import json
import re
import argparse

# 10 atomic rules
SELECTED = {
    "REQ-117.130-001A",
    "REQ-117.130-001B",
    "REQ-117.130-001C",
    "REQ-117.130-001D",
    "REQ-117.130-001F",
    "REQ-117.130-002A",
    "REQ-117.130-002B",
    "REQ-117.130-002C",
    "REQ-117.130-003A",
    "REQ-117.130-003B",
}

# ---------- Arguments ----------
parser = argparse.ArgumentParser(description="Generate requirement JSON from CFR Markdown")
parser.add_argument("--input", "-i", required=True, help="Input Markdown file (.md)")
parser.add_argument("--output", "-o", required=True, help="Output JSON file")
parser.add_argument("--cfr", "-c", required=True, help="CFR section (e.g., 21 CFR 117.130)")
parser.add_argument("--structure", "-s", help="Output expected structure JSON")
args = parser.parse_args()

INPUT_MD = args.input
OUTPUT_JSON = args.output
OUTPUT_STRUCTURE = args.structure
CFR_SECTION = args.cfr

# ---------- Read File ----------
with open(INPUT_MD, "r") as f:
    lines = [line.strip() for line in f if line.strip()]

requirements = []
current_req = None
expected_structure = {}

# ---------- Parse ----------
for line in lines:

    # Capture REQ ID
    req_match = re.search(r"→\s*(REQ-[\d\.]+-\d+)", line)
    if req_match:
        current_req = req_match.group(1)
        continue

    # Capture atomic rules
    atomic_match = re.match(r"^(.*?)\s*→\s*([A-Z]\d*)$", line)
    if atomic_match and current_req:
        description = atomic_match.group(1).strip()
        suffix = atomic_match.group(2)

        requirement_id = f"{current_req}{suffix}"

        # Parent logic
        if len(suffix) == 1:
            parent = current_req
        else:
            parent = f"{current_req}{suffix[0]}"

        # expected_structure.json mapping
        expected_structure.setdefault(current_req, set()).add(suffix[0])

        requirements.append({
            "requirement_id": requirement_id,
            "description": description,
            "source": CFR_SECTION,
            "parent": parent
        })

# ---------- Save ----------
with open(OUTPUT_JSON, "w") as f:
    json.dump(requirements, f, indent=2)

print(f"Saved {len(requirements)} requirements → {OUTPUT_JSON}")

# ---------- Save expected_structure.json ----------
if args.structure:
    # Use only the selected requirements
    selected_structure = {}
    for rid in SELECTED:
        m = re.match(r"^(REQ-[\d\.]+-\d+)([A-Z])", rid)
        if m:
            parent_req, letter = m.group(1), m.group(2)
            selected_structure.setdefault(parent_req, set()).add(letter)

    expected_structure_json = {
        parent_req: sorted(list(child_letters))
        for parent_req, child_letters in selected_structure.items()
    }
    with open(OUTPUT_STRUCTURE, "w") as f:
        items = list(expected_structure_json.items())
        f.write("{\n")
        for i, (parent_req, child_letters) in enumerate(items):
            key = json.dumps(parent_req)
            val = json.dumps(child_letters, separators=(", ", ": "))
            comma = "," if i < len(items) - 1 else ""
            f.write(f"  {key}: {val}{comma}\n")
        f.write("}\n")

    print(f"Saved expected structure: {OUTPUT_STRUCTURE}")
