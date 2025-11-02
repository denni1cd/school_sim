from pathlib import Path

import pytest

from bootstrap import load_rooms, load_students, load_timetable
from save_system import SaveSystem
from world import World


def test_m3_save_roundtrip(tmp_path: Path):
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    world = World(rooms, students, timetable)
    save_system = SaveSystem(tmp_path)

    result = save_system.save(world)
    assert result.path.exists()

    # mutate world to ensure load restores original snapshot
    world.time_minutes += 42
    for student in world.students:
        student.needs["hunger"] = 99.0

    save_system.load(result.path, world)
    assert world.time_minutes == result.snapshot["time_minutes"]
    for stored, student in zip(result.snapshot["students"], world.students):
        assert pytest.approx(stored["needs"]["hunger"]) == student.needs["hunger"]
