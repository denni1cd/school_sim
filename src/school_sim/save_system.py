from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, Optional


@dataclass
class SaveResult:
    path: Path
    snapshot: dict


class SaveSystem:
    def __init__(self, save_dir: Path | str = Path("runtime/saves")):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def snapshot_world(self, world) -> dict:
        """Convert the current world state into a serializable snapshot."""
        students = []
        for student in world.students:
            students.append(
                {
                    "name": student.name,
                    "room": student.current_room,
                    "target": student.target_room,
                    "needs": {k: float(v) for k, v in student.needs.items()},
                }
            )
        return {
            "time_minutes": int(world.time_minutes),
            "students": students,
        }

    def save(self, world) -> SaveResult:
        """Persist the world snapshot to disk and return the result metadata."""
        snapshot = self.snapshot_world(world)
        filename = datetime.now(UTC).strftime("save_%Y%m%d_%H%M%S.json")
        path = self.save_dir / filename
        with path.open("w", encoding="utf-8") as handle:
            json.dump(snapshot, handle, indent=2, sort_keys=True)
        return SaveResult(path=path, snapshot=snapshot)

    def load(self, path: Path | str, world) -> dict:
        """Load the specified snapshot and apply it to the world."""
        snapshot = self._read_snapshot(Path(path))
        self.apply_snapshot(world, snapshot)
        return snapshot

    def load_latest(self, world) -> Optional[Path]:
        """Load the most recently created save file."""
        saves = sorted(self.save_dir.glob("save_*.json"))
        if not saves:
            return None
        latest = saves[-1]
        self.load(latest, world)
        return latest

    def apply_snapshot(self, world, snapshot: dict) -> None:
        """Mutate the world to match the provided snapshot."""
        self._validate_snapshot(snapshot)
        world.time_minutes = int(snapshot["time_minutes"])
        student_lookup: Dict[str, any] = {student.name: student for student in world.students}
        for entry in snapshot["students"]:
            student = student_lookup.get(entry["name"])
            if not student:
                continue
            room_name = entry.get("room") or student.current_room
            if room_name not in world.rooms:
                room_name = student.current_room
            student.current_room = room_name
            student.target_room = entry.get("target")
            needs = entry.get("needs", {})
            for need_name, value in needs.items():
                student.needs[need_name] = _clamp(float(value))
            # reposition student at room center
            room = world.rooms.get(student.current_room)
            if room:
                student.x = room.x + room.width / 2.0
                student.y = room.y + room.height / 2.0

    def _read_snapshot(self, path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(f"Save file not found: {path}")
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _validate_snapshot(self, snapshot: dict) -> None:
        if "time_minutes" not in snapshot or "students" not in snapshot:
            raise ValueError("Snapshot missing required keys.")
        if not isinstance(snapshot["students"], list):
            raise ValueError("Snapshot students must be a list.")
        for entry in snapshot["students"]:
            if "name" not in entry or "needs" not in entry:
                raise ValueError("Snapshot student entries must include name and needs.")


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))
