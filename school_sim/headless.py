"""Headless simulation runner that writes deterministic logs for automation."""
from __future__ import annotations

import argparse
from pathlib import Path

from .bootstrap import (
    load_clubs_config,
    load_curriculum_config,
    load_game_config,
    load_policies_config,
    load_rooms,
    load_students,
    load_timetable,
)
from .events.event_bus import EventBus
from .events.event_loader import load_events
from .events.event_rules import EventRules
from .save_system import SaveSystem
from .world import World

PACKAGE_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_ROOT / "configs"
RUNTIME_DIR = PACKAGE_ROOT / "runtime"
DEFAULT_LOG_PATH = RUNTIME_DIR / "logs" / "sim_log.txt"


def run_headless(
    ticks: int = 300,
    *,
    log_path: Path = DEFAULT_LOG_PATH,
    load_path: Path | None = None,
) -> Path:
    """Run the simulation without rendering and emit the deterministic log file."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    game_config = load_game_config()
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    event_bus = EventBus()
    policies_config = load_policies_config()
    clubs_config = load_clubs_config()
    curriculum_config = load_curriculum_config()
    world = World(
        rooms,
        students,
        timetable,
        event_bus=event_bus,
        game_config=game_config,
        policy_config=policies_config,
        clubs_config=clubs_config,
        curriculum_config=curriculum_config,
    )

    events_catalog = load_events(CONFIG_DIR / "events.yaml")
    rules = EventRules(events_catalog, event_bus)
    rules.bind_world(world)

    save_system = SaveSystem(RUNTIME_DIR / "saves")
    world.save_system = save_system
    if load_path:
        save_system.load(load_path, world)

    with log_path.open("w", encoding="utf-8") as handle:
        for _ in range(ticks):
            world.tick(dt_minutes=1)
            snapshot = world.get_debug_snapshot()

            policy_snapshot = snapshot.get("policy", {})
            curriculum_snapshot = snapshot.get("curriculum", {})
            breakdown = snapshot.get("rating_breakdown", {})
            handle.write(
                "STATUS,{time},{rating:.2f},{budget},{uniforms},{discipline},{track},{needs:.2f},{compliance:.2f},{clubs:.2f},{attendance:.2f}\n".format(
                    time=snapshot["time"],
                    rating=float(snapshot.get("rating", 0.0)),
                    budget=int(snapshot.get("budget", 0)),
                    uniforms=policy_snapshot.get("uniforms", "moderate"),
                    discipline=policy_snapshot.get("discipline", "fair"),
                    track=curriculum_snapshot.get("active_track", "General"),
                    needs=float(breakdown.get("needs", 0.0)),
                    compliance=float(breakdown.get("compliance", 0.0)),
                    clubs=float(breakdown.get("clubs", 0.0)),
                    attendance=float(breakdown.get("attendance", 0.0)),
                )
            )

            rating_delta = float(snapshot.get("rating_delta", 0.0))
            if abs(rating_delta) > 0.0:
                handle.write(
                    f"RATING,{snapshot['time']},{snapshot['rating']:.2f},{rating_delta:+.2f}\n"
                )

            for event in snapshot.get("events", []):
                handle.write(
                    f"EVENT,{event.get('time')},{event.get('id')},{(event.get('caption') or '').strip()}\n"
                )

            for student in sorted(snapshot["students"], key=lambda entry: entry["name"]):
                needs = student["needs"]
                handle.write(
                    f"{snapshot['time']},{student['name']},{student['room']},{student['target'] or '-'},"
                    f"{needs['hunger']:.1f},{needs['energy']:.1f},{needs['stress']:.1f},{needs['hygiene']:.1f}\n"
                )
    return log_path


def main() -> None:
    """CLI entry point that parses args and runs the headless loop."""
    parser = argparse.ArgumentParser(description="Run the school simulation in headless mode.")
    parser.add_argument("--ticks", type=int, default=300, help="Number of ticks to simulate (default: 300).")
    parser.add_argument("--load", type=Path, help="Optional save file to load before simulation.")
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH, help="Path for the output log file.")
    args = parser.parse_args()

    run_headless(ticks=args.ticks, log_path=args.log_path, load_path=args.load)


if __name__ == "__main__":
    main()

