# scripts/validate_vaults.py
import json
import re
import sys

def validate():
    with open("doc/src/data/vaultRegistry.js", "r", encoding="utf-8") as f:
        content = f.read()

    # Extract JSON object
    match = re.search(r"export const VAULT_REGISTRY = (\{.*\});", content, re.DOTALL)
    if not match:
        print("❌ Could not parse VAULT_REGISTRY from JS file")
        sys.exit(1)

    data = json.loads(match.group(1))
    print(f"🔍 Validating {len(data)} module entries in vaultRegistry.js...")

    errors = []
    for mod_id, val in data.items():
        if "questions" not in val:
            errors.append(f"Module {mod_id} missing 'questions'")
            continue
        qs = val["questions"]
        if len(qs) < 3:
            errors.append(f"Module {mod_id} has only {len(qs)} questions (expected >= 3)")
        for i, q in enumerate(qs):
            if not q.get("question"):
                errors.append(f"Module {mod_id} Q{i+1} empty question string")
            options = q.get("options", [])
            if len(options) != 4:
                errors.append(f"Module {mod_id} Q{i+1} options length is {len(options)} (expected 4)")
            correct = q.get("correctIndex")
            if correct not in [0, 1, 2, 3]:
                errors.append(f"Module {mod_id} Q{i+1} invalid correctIndex {correct}")
            if not q.get("hint"):
                errors.append(f"Module {mod_id} Q{i+1} missing hint")

    if errors:
        print(f"❌ Found {len(errors)} validation errors:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print(f"✅ All {len(data)} modules passed schema and question integrity checks with ZERO errors!")

if __name__ == "__main__":
    validate()
