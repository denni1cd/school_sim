from pathlib import Path

import json
import pytest

from bootstrap import load_rooms, load_students, load_timetable
from save_system import SaveSystem
from world import World


def build_world():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    return World(rooms, students, timetable)


def test_save_load_roundtrip(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path)

    result = system.save(world)
    world.time_minutes += 25
    for student in world.students:
        student.needs["hunger"] = 99.0

    system.load(result.path, world)

    assert world.time_minutes == result.snapshot["time_minutes"]
    for snapshot_student, student in zip(result.snapshot["students"], world.students):
        assert pytest.approx(snapshot_student["needs"]["hunger"]) == student.needs["hunger"]
        assert snapshot_student["room"] == student.current_room


def test_load_latest_handles_missing(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path)

    latest = system.load_latest(world)
    assert latest is None


def test_invalid_snapshot_raises(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path)
    bad_snapshot = tmp_path / "bad.json"
    bad_snapshot.write_text(json.dumps({"students": []}), encoding="utf-8")

    with pytest.raises(ValueError):
        system.load(bad_snapshot, world)
