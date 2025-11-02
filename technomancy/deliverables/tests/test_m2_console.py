import pygame

from events.event_bus import EventBus
from events.event_models import Event
from principal_console import PrincipalConsole


class DummyWorld:
    def __init__(self):
        self.time_minutes = 8 * 60
        self.calls = []

    def tick(self, dt_minutes: int = 1):
        self.calls.append(dt_minutes)
        self.time_minutes += dt_minutes


def test_console_actions_reference():
    bus = EventBus()
    event = Event(id="assembly", when="08:15")
    console = PrincipalConsole(bus, [event])
    world = DummyWorld()

    triggered = []
    bus.subscribe("event_fired", lambda payload: triggered.append(payload["event"].id))

    console.toggle()
    console.handle_key(pygame.K_t, world)
    console.handle_key(pygame.K_e, world)
    console.handle_key(pygame.K_b, world)

    assert world.calls == [15]
    assert triggered == ["assembly"]
    assert len(console.log) >= 3
