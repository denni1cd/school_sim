import pytest
import pygame

from school_sim.bootstrap import CONFIG_DIR, load_game_config, load_rooms, load_students, load_timetable
from school_sim.events.event_bus import EventBus
from school_sim.events.event_loader import load_events
from school_sim.events.event_rules import EventRules
from school_sim.events.scene_overlay import SceneOverlay
from school_sim.principal_console import PrincipalConsole
from school_sim.renderer import Renderer
from school_sim.world import World


def test_renderer_hud_exposes_metrics(tmp_path):
    pygame.init()
    game_config = load_game_config()
    rooms = load_rooms()
    students = load_students()
    timetable = load_timetable()
    bus = EventBus()
    overlay = SceneOverlay(base_dir=str(tmp_path))
    events_catalog = load_events(CONFIG_DIR / "events.yaml")
    overlay.attach(pygame.Surface((128, 128)))
    overlay.bind(bus)

    world = World(rooms, students, timetable, event_bus=bus, game_config=game_config)
    rules = EventRules(events_catalog, bus)
    rules.bind_world(world)

    console = PrincipalConsole(bus, events_catalog)
    renderer = Renderer(rooms, students, overlay, console)

    try:
        snapshot = world.get_debug_snapshot()
        renderer.draw(snapshot)
        metrics = renderer._last_hud_metrics
        assert metrics["time"] == snapshot["time"]
        assert metrics["rating"] == pytest.approx(world.rating)
        assert metrics["budget"] == world.budget
        assert metrics["delta"] == pytest.approx(snapshot.get("rating_delta", 0.0))
        assert metrics["flash"] is False
    finally:
        pygame.quit()
