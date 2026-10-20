"""Read structured exports after running python scripts/build.py."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1] / "dist"
sensitive = json.loads((root / "sensitive/terms.json").read_text(encoding="utf-8"))
entities = json.loads((root / "entities/entities.json").read_text(encoding="utf-8"))

for record in sensitive:
    print(record["id"], record["term"], record["assessments"])

for record in entities:
    print(record["id"], record["entity_type"], record["names"])

print(f"Loaded {len(sensitive)} sensitive terms and {len(entities)} named entities.")
