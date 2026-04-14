import argparse
import json

def load_json(path: str):
    with open(path, "r") as f:
        return json.load(f)
        
def main() -> None:
    parser = argparse.ArgumentParser(description="Generate minimal test cases from requirements + expected structure")
    parser.add_argument("--requirements", "-r", required=True, help="Input requirements JSON (list)")
    parser.add_argument("--structure", "-s", required=True, help="Input expected_structure.json (mapping)")
    parser.add_argument("--output", "-o", required=True, help="Output test_cases.json path")
    args = parser.parse_args()
    
    requirements = load_json(args.requirements)
    structure = load_json(args.structure)
    
    req_by_id = {r.get("requirement_id"): r for r in requirements if isinstance(r, dict)}
    
    selected_ids = []
    for parent_id in sorted(structure.keys()):
        letters = structure[parent_id] or []
        for letter in sorted(letters):
            selected_ids.append(f"{parent_id}{letter}")
    
    test_cases = []
    for i, rid in enumerate(selected_ids, start=1):
        req = req_by_id.get(rid, {})
        req_desc = (req.get("description") or "").strip()
        if req_desc:
            description = f"{req_desc.rstrip('.')}."
        else:
            description = "Verify that the requirement is satisfied."

        test_cases.append(
            {
                "test_case_id": f"TC-{i:03d}",
                "requirement_id": rid,
                "description": description,
            }
        )

    with open(args.output, "w") as f:
        json.dump(test_cases, f, indent=2)

    print(f"Saved {len(test_cases)} test cases → {args.output}")


if __name__ == "__main__":
    main()