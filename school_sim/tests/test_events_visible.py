from pathlib import Path

import pygame

from school_sim.bootstrap import CONFIG_DIR, load_game_config, load_rooms, load_students, load_timetable
from school_sim.events.event_bus import EventBus
from school_sim.events.event_loader import load_events
from school_sim.events.event_rules import EventRules
from school_sim.events.scene_overlay import SceneOverlay
from school_sim.world import World


def _build_world() -> tuple[World, SceneOverlay]:
    game_config = load_game_config()
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()

    bus = EventBus()
    overlay = SceneOverlay(base_dir=str(Path(CONFIG_DIR.parent, "runtime", "scenes")))
    overlay.attach(pygame.Surface((200, 150)))
    overlay.bind(bus)

    world = World(rooms, students, timetable, event_bus=bus, game_config=game_config)
    events_catalog = load_events(CONFIG_DIR / "events.yaml")
    rules = EventRules(events_catalog, bus)
    rules.bind_world(world)
    return world, overlay


def test_welcome_event_triggers_overlay_at_0802():
    pygame.init()
    world, overlay = _build_world()

    assert not overlay.is_active
    assert world.event_history == []

    world.tick(dt_minutes=1)
    assert not overlay.is_active

    world.tick(dt_minutes=1)
    assert overlay.is_active
    assert overlay.caption == "Welcome assembly in the gym."

    events = world.event_history
    assert any(event["id"] == "welcome_assembly" for event in events)
    assert events[-1]["time"] == "08:02"

    # Ensure overlay dismisses on ESC
    overlay.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    assert not overlay.is_active

