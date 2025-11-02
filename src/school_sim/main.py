import argparse
from pathlib import Path

import pygame

from .bootstrap import load_rooms, load_students, load_timetable
from .events.event_bus import EventBus
from .events.event_loader import load_events
from .events.event_rules import EventRules
from .events.scene_overlay import SceneOverlay
from .principal_console import PrincipalConsole
from .renderer import Renderer
from .save_system import SaveSystem
from .world import World


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive School Simulation")
    parser.add_argument("--load", type=Path, help="Optional save file to load at startup.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    event_bus = EventBus()
    events_catalog = load_events("configs/events.yaml")

    world = World(rooms, students, timetable, event_bus=event_bus)
    overlay = SceneOverlay(base_dir="runtime/scenes")
    overlay.bind(event_bus)
    console = PrincipalConsole(event_bus, events_catalog)
    save_system = SaveSystem()
    renderer = Renderer(rooms, students, overlay, console, save_system=save_system)

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
    while running:
        running = renderer.process_events(world)

        world.tick(dt_minutes=10)
        snapshot = world.get_debug_snapshot()

        print("\n" + "=" * 60)
        print(f"Time: {snapshot['time']}")
        for student in snapshot["students"]:
            print(
                f"{student['name']:6} | room={student['room']:10} -> target={student['target']:10} "
                f"| hunger={student['needs']['hunger']:.1f} energy={student['needs']['energy']:.1f} "
                f"stress={student['needs']['stress']:.1f} | discipline_risk={student['discipline_risk']:.1f}"
            )

        renderer.draw(snapshot["time"])
        clock.tick(2)

    pygame.quit()


if __name__ == "__main__":
    main()
