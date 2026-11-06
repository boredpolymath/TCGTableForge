#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "fixtures" / "performance-500-1000.json"
TYPES = ["World", "Experience", "Theme", "Mechanic", "Question"]
STAMP = datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
PROJECT_ID = "performance-project"

cards = [{
    "cardId": f"card-{i:04d}", "projectId": PROJECT_ID, "type": TYPES[i % len(TYPES)],
    "title": f"Fixture idea {i:04d}", "notes": ("Large note fixture. " * 150) if i == 0 else f"Repeatable performance fixture note {i:04d}.",
    "createdAt": STAMP, "updatedAt": STAMP
} for i in range(500)]
relationships = [{
    "relationshipId": f"relationship-{i:04d}", "projectId": PROJECT_ID,
    "fromCardId": cards[i % 500]["cardId"], "toCardId": cards[(i + 1 + i // 500) % 500]["cardId"],
    "label": ["Supports", "Expresses", "Creates Tension With", "Depends On"][i % 4],
    "createdAt": STAMP
} for i in range(1000)]
project = {
    "projectId": PROJECT_ID, "name": "Performance Fixture", "approach": "world-first",
    "description": "Generated 500-card and 1,000-relationship fixture.", "designGoals": "Repeatable local performance measurements.",
    "customRelationshipLabels": [], "createdAt": STAMP, "updatedAt": STAMP,
    "cards": cards, "relationships": relationships
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"schemaVersion": 1, "project": project}, indent=2) + "\n")
print(f"Wrote {OUT.relative_to(ROOT)}")
