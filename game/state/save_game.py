from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Mapping, Sequence

from ..simulation.schedule_generator import ScheduleAssignment, ScheduleTemplate


def serialize_assignments(assignments: Sequence[ScheduleAssignment]) -> List[dict]:
    return [assignment.to_dict() for assignment in assignments]


def save_schedule_assignments(path: str | Path, assignments: Sequence[ScheduleAssignment]) -> None:
    output_path = Path(path)
    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"assignments": serialize_assignments(assignments)}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_schedule_assignments(
    path: str | Path,
    templates: Mapping[str, ScheduleTemplate],
) -> List[ScheduleAssignment]:
    source = Path(path)
    if not source.exists():
        return []
    payload = json.loads(source.read_text(encoding="utf-8"))
    entries = payload.get("assignments", [])
    if not isinstance(entries, Iterable):
        return []
    assignments: List[ScheduleAssignment] = []
    for entry in entries:
        if isinstance(entry, Mapping):
            assignments.append(ScheduleAssignment.from_dict(entry, templates=templates))
    return assignments


__all__ = [
    "serialize_assignments",
    "save_schedule_assignments",
    "load_schedule_assignments",
]
