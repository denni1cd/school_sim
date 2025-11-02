import pygame

from events.event_bus import EventBus
from events.event_models import Event
from principal_console import PrincipalConsole


class DummyWorld:
    def __init__(self):
        self.time_minutes = 8 * 60
        self.tick_calls = []

    def tick(self, dt_minutes: int = 1):
        self.tick_calls.append(dt_minutes)
        self.time_minutes += dt_minutes


def test_console_advances_time_and_logs():
    bus = EventBus()
    console = PrincipalConsole(bus, [])
    world = DummyWorld()

    console.toggle()
    console.handle_key(pygame.K_t, world)

    assert world.tick_calls == [15]
    assert console.log[0].startswith("Advanced time")


def test_console_triggers_first_event():
    bus = EventBus()
    event = Event(id="assembly", when="08:15")
    console = PrincipalConsole(bus, [event])
    world = DummyWorld()

    triggered = []
    bus.subscribe("event_fired", lambda payload: triggered.append(payload["event"].id))

    console.toggle()
    console.handle_key(pygame.K_e, world)

    assert triggered == ["assembly"]
    assert console.log[0] == "Triggered event 'assembly'."
