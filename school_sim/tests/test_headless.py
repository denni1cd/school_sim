"""Run the headless simulation runner to keep deterministic logs."""

from pathlib import Path

from school_sim.bootstrap import load_rooms, load_students, load_timetable
from school_sim.headless import run_headless
from school_sim.save_system import SaveSystem
from school_sim.world import World


def build_world():
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    return World(rooms, students, timetable)


def test_headless_generates_log(tmp_path: Path):
    log_path = tmp_path / "log.txt"
    run_headless(ticks=5, log_path=log_path)
    lines = log_path.read_text(encoding="utf-8").splitlines()
    status_lines = [line for line in lines if line.startswith("STATUS")]
    assert status_lines, "headless log should emit STATUS lines with curriculum state"
    parts = status_lines[0].split(",")
    assert parts[0] == "STATUS"
    assert len(parts) == 11
    assert parts[6] in {"General", "STEM", "Arts"}
    for idx in range(7, 11):
        float(parts[idx])


def test_headless_loads_save(tmp_path: Path):
    world = build_world()
    system = SaveSystem(tmp_path / "saves")
    save_path = system.save(world).path

    log_path = tmp_path / "log.txt"
    run_headless(ticks=3, log_path=log_path, load_path=save_path)
    assert log_path.exists()
