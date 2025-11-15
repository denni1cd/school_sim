"""Entrypoint for the interactive School Sim experience."""

import argparse
import os
from pathlib import Path

import pygame

from .bootstrap import (
    load_clubs_config,
    load_curriculum_config,
    load_game_config,
    load_policies_config,
    load_rooms,
    load_staff_config,
    load_students,
    load_timetable,
)
from .events.event_bus import EventBus
from .events.event_loader import load_events
from .events.event_rules import EventRules
from .events.scene_overlay import SceneOverlay
from .office import OfficeScreen
from .principal_console import PrincipalConsole
from .renderer import Renderer
from .save_system import SaveSystem
from .world import World

PACKAGE_ROOT = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_ROOT / "configs"
RUNTIME_DIR = PACKAGE_ROOT / "runtime"


def parse_args() -> argparse.Namespace:
    """Return parsed CLI arguments (currently only --load)."""
    parser = argparse.ArgumentParser(description="Interactive School Simulation")
    parser.add_argument("--load", type=Path, help="Optional save file to load at startup.")
    return parser.parse_args()


def main() -> None:
    """Compose all simulation services and start the interactive loop."""
    args = parse_args()

    game_config = load_game_config()
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    event_bus = EventBus()
    events_catalog = load_events(CONFIG_DIR / "events.yaml")

    policies_config = load_policies_config()
    clubs_config = load_clubs_config()
    curriculum_config = load_curriculum_config()
    staff_config = load_staff_config()

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
    overlay = SceneOverlay(base_dir=str(RUNTIME_DIR / "scenes"))
    overlay.bind(event_bus)
    console = PrincipalConsole(event_bus, events_catalog)
    office = OfficeScreen(
        policies=policies_config,
        clubs=clubs_config,
        curriculum=curriculum_config,
        staff=staff_config,
    )
    save_system = SaveSystem(RUNTIME_DIR / "saves")
    world.save_system = save_system
    office.bind_world(world)
    renderer = Renderer(
        rooms,
        students,
        overlay,
        console,
        office=office,
        save_system=save_system,
    )

    rules = EventRules(events_catalog, event_bus)
    rules.bind_world(world)

    if args.load:
        try:
            save_system.load(args.load, world)
            console.record(f"Loaded save {args.load.name}.")
        except FileNotFoundError:
            console.record(f"Save file not found: {args.load}")
        except ValueError as exc:
            console.record(f"Failed to load save: {exc}")

    clock = pygame.time.Clock()
    running = True
    max_loops_env = os.getenv("SCHOOL_SIM_MAX_LOOPS")
    max_loops = None
    if max_loops_env:
        try:
            parsed = int(max_loops_env)
            if parsed > 0:
                max_loops = parsed
        except ValueError:
            console.record(f"Ignoring invalid SCHOOL_SIM_MAX_LOOPS value: {max_loops_env}")
    loop_count = 0
    while running:
        running = renderer.process_events(world)

        world.tick(dt_minutes=10)
        snapshot = world.get_debug_snapshot()

        print("\n" + "=" * 60)
        print(f"Time: {snapshot['time']}")
        print(f"Rating: {snapshot['rating']:.1f} | Budget: {snapshot['budget']}")
        for student in snapshot["students"]:
            print(
                f"{student['name']:6} | room={student['room']:10} -> target={student['target']:10} "
                f"| hunger={student['needs']['hunger']:.1f} energy={student['needs']['energy']:.1f} "
                f"stress={student['needs']['stress']:.1f} | discipline_risk={student['discipline_risk']:.1f}"
            )

        renderer.draw(snapshot)
        clock.tick(2)
        loop_count += 1
        if max_loops is not None and loop_count >= max_loops:
            console.record("Auto-stopping interactive run (loop limit reached).")
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
