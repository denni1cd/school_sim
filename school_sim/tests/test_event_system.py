"""Exercise the event bus and rule evaluation logic."""

import pygame
import pytest

from school_sim.events.event_bus import EventBus
from school_sim.events.event_loader import load_events
from school_sim.events.event_models import Event, EventValidationError, Scene
from school_sim.events.event_rules import EventRules
from school_sim.events.scene_overlay import SceneOverlay


def test_event_loader_validates_time(tmp_path):
    events_file = tmp_path / "events.yaml"
    events_file.write_text(
        """
        - id: time_test
          when: "08:30"
          scene:
            image: welcome.png
            caption: hello
        """
    )

    events = load_events(str(events_file))
    assert events[0].id == "time_test"
    assert events[0].scene.image == "welcome.png"


def test_event_loader_rejects_bad_time(tmp_path):
    events_file = tmp_path / "events.yaml"
    events_file.write_text(
        """
        - id: bad
          when: "8:3"
        """
    )

    with pytest.raises(EventValidationError):
        load_events(str(events_file))


def test_time_and_condition_event_fires_once():
    bus = EventBus()
    event = Event(
        id="critical_hunger",
        when="08:00",
        condition="student in homeroom_A and needs.hunger >= 85",
        once=True,
    )
    rules = EventRules([event], bus)

    captured = []
    bus.subscribe("event_fired", lambda payload: captured.append(payload["event"].id))

    student = type("Student", (), {"homeroom": "homeroom_A", "needs": {"hunger": 90}, "current_room": "ClassroomA"})
    world = type("World", (), {"students": [student], "rooms": {"ClassroomA": object()}, "time_minutes": 8 * 60})
    rules.bind_world(world)

    bus.emit("time_tick", {"time_minutes": 8 * 60, "time_str": "08:00"})
    bus.emit("time_tick", {"time_minutes": 8 * 60, "time_str": "08:00"})

    assert captured == ["critical_hunger"]


def test_room_event_fires_on_room_enter():
    bus = EventBus()
    event = Event(id="lounge_break", room="Lounge")
    rules = EventRules([event], bus)
    captured = []
    bus.subscribe("event_fired", lambda payload: captured.append(payload["room"]))
    student = type("Student", (), {"homeroom": "homeroom_A", "needs": {}, "current_room": "Lounge"})
    world = type("World", (), {"students": [student], "rooms": {"Lounge": object()}, "time_minutes": 9 * 60})
    rules.bind_world(world)

    bus.emit("room_enter", {"room": "Lounge", "student": student})

    assert captured == ["Lounge"]


def test_scene_overlay_reacts_to_event(tmp_path):
    pygame.display.init()
    try:
        screen = pygame.display.set_mode((100, 100))
        bus = EventBus()
        overlay = SceneOverlay(str(tmp_path))
        overlay.attach(screen)
        overlay.bind(bus)

        image_path = tmp_path / "scene.png"
        pygame.image.save(pygame.Surface((10, 10)), str(image_path))
        event = Event(id="scene_event", scene=Scene(image=image_path.name, caption="Hello"))
        bus.emit("event_fired", {"event": event})

        assert overlay.active
        assert overlay.caption == "Hello"

        overlay.hide()
        assert not overlay.active
    finally:
        pygame.display.quit()
