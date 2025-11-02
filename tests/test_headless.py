from pathlib import Path

from headless import run_headless
from save_system import SaveSystem
from world import World
from bootstrap import load_rooms, load_students, load_timetable


def build_world():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    return World(rooms, students, timetable)


def test_headless_generates_log(tmp_path: Path):
    log_path = tmp_path / "log.txt"
    run_headless(ticks=5, log_path=log_path)
    contents = log_path.read_text(encoding="utf-8").splitlines()
    assert len(contents) > 0
    parts = contents[0].split(",")
    assert len(parts) == 8


def test_headless_loads_save(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path / "saves")
    save_path = system.save(world).path

    log_path = tmp_path / "log.txt"
    run_headless(ticks=3, log_path=log_path, load_path=save_path)
    assert log_path.exists()
