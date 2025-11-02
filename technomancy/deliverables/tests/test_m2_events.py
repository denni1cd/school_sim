import pygame
import pytest

from events.event_bus import EventBus
from events.event_loader import load_events
from events.event_models import Event, EventValidationError, Scene
from events.event_rules import EventRules
from events.scene_overlay import SceneOverlay


def test_loader_and_rules_sample(tmp_path):
    config = tmp_path / "events.yaml"
    config.write_text(
        """
        - id: assembly
          when: "08:15"
          scene:
            image: welcome.png
            caption: "Morning assembly."
        """
    )
    events = load_events(str(config))
    assert events[0].id == "assembly"

    bus = EventBus()
    rules = EventRules(events, bus)
    world = type("World", (), {"students": [], "rooms": {}, "time_minutes": 8 * 60 + 15})
    rules.bind_world(world)

    payloads = []
    bus.subscribe("event_fired", lambda payload: payloads.append(payload))
    bus.emit("time_tick", {"time_minutes": world.time_minutes, "time_str": "08:15"})

    assert payloads and payloads[0]["event"].id == "assembly"


def test_invalid_time_raises(tmp_path):
    config = tmp_path / "events.yaml"
    config.write_text("- id: bad\n  when: '8:3'\n")
    with pytest.raises(EventValidationError):
        load_events(str(config))


def test_overlay_reacts(tmp_path):
    pygame.display.init()
    try:
        screen = pygame.display.set_mode((80, 80))
        bus = EventBus()
        overlay = SceneOverlay(str(tmp_path))
        overlay.attach(screen)
        overlay.bind(bus)

        image_path = tmp_path / "scene.png"
        pygame.image.save(pygame.Surface((10, 10)), str(image_path))
        event = Event(id="overlay", scene=Scene(image=image_path.name, caption="Test"))
        bus.emit("event_fired", {"event": event})

        assert overlay.active
    finally:
        pygame.display.quit()
