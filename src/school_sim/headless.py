"""
Headless simulation runner that produces deterministic logs for Milestone M3.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .bootstrap import load_rooms, load_students, load_timetable
from .events.event_bus import EventBus
from .events.event_loader import load_events
from .events.event_rules import EventRules
from .save_system import SaveSystem
from .world import World

DEFAULT_LOG_PATH = Path("runtime/logs/sim_log.txt")


def run_headless(
    ticks: int = 300,
    *,
    log_path: Path = DEFAULT_LOG_PATH,
    load_path: Path | None = None,
) -> Path:
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    event_bus = EventBus()
    world = World(rooms, students, timetable, event_bus=event_bus)

    events_catalog = load_events("configs/events.yaml")
    rules = EventRules(events_catalog, event_bus)
    rules.bind_world(world)

    save_system = SaveSystem()
    if load_path:
        save_system.load(load_path, world)

    with log_path.open("w", encoding="utf-8") as handle:
        for _ in range(ticks):
            world.tick(dt_minutes=1)
            snapshot = world.get_debug_snapshot()
            for student in sorted(snapshot["students"], key=lambda entry: entry["name"]):
                needs = student["needs"]
                handle.write(
                    f"{snapshot['time']},{student['name']},{student['room']},{student['target'] or '-'},"
                    f"{needs['hunger']:.1f},{needs['energy']:.1f},{needs['stress']:.1f},{needs['hygiene']:.1f}\n"
                )
    return log_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the school simulation in headless mode.")
    parser.add_argument("--ticks", type=int, default=300, help="Number of ticks to simulate (default: 300).")
    parser.add_argument("--load", type=Path, help="Optional save file to load before simulation.")
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH, help="Path for the output log file.")
    args = parser.parse_args()

    run_headless(ticks=args.ticks, log_path=args.log_path, load_path=args.load)


if __name__ == "__main__":
    main()
