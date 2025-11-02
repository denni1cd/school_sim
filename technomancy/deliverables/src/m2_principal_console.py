"""
Principal Console reference outline for Milestone M2.

The production implementation lives in `principal_console.PrincipalConsole`.
"""
from __future__ import annotations

import pygame

from events.event_bus import EventBus
from events.event_models import Event


class PrincipalConsoleReference:
    def __init__(self, bus: EventBus, events: list[Event]):
        self.bus = bus
        self.events = events
        self.visible = False
        self.log: list[str] = []

    def toggle(self) -> None:
        self.visible = not self.visible

    def handle_key(self, key: int, world) -> None:
        if key == pygame.K_t:
            world.tick(dt_minutes=15)
            self.log.append("Advanced time by 15 minutes.")
        elif key == pygame.K_e and self.events:
            event = self.events[0]
            self.bus.emit(
                "event_fired",
                {
                    "event": event,
                    "time_minutes": world.time_minutes,
                    "time_str": f"{world.time_minutes // 60:02d}:{world.time_minutes % 60:02d}",
                    "room": None,
                    "student": None,
                    "trigger": "console",
                },
            )
            self.log.append(f"Triggered event '{event.id}'.")
        elif key == pygame.K_b:
            self.log.append("Campus broadcast placeholder triggered.")
