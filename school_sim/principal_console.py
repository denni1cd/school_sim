"""Principal Console overlay controls for debugging actions."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Deque, List, Optional

import pygame

from .events.event_bus import EventBus
from .events.event_models import Event
from .timetable import minutes_to_timestr


class PrincipalConsole:
    """Manage the Principal Console overlay, including shortcuts and logs."""

    def __init__(self, event_bus: EventBus, events_catalog: List[Event]):
        """Initialize with the event bus and catalog for triggering events."""
        self.event_bus = event_bus
        self.events_catalog = events_catalog
        self.visible = False
        self.log: Deque[str] = deque(maxlen=10)

    def toggle(self) -> None:
        """Toggle the visibility of the console overlay."""
        self.visible = not self.visible

    def handle_key(self, key: int, world) -> None:
        """Translate console shortcuts into world actions."""
        if key == pygame.K_t:
            self._advance_time(world, 15)
        elif key == pygame.K_e:
            self._trigger_first_event(world)
        elif key == pygame.K_b:
            self._broadcast()
        elif key == pygame.K_s:
            self._save_snapshot(world)
        elif key == pygame.K_l:
            self._load_latest(world)

    def record(self, message: str) -> None:
        """Add a message to the console log."""
        self.log.appendleft(message)

    def _advance_time(self, world, minutes: int) -> None:
        world.tick(dt_minutes=minutes)
        self.record(f"Advanced time by {minutes} minutes.")

    def _trigger_first_event(self, world) -> None:
        event = self._first_event()
        if not event:
            self.record("No events available to trigger.")
            return
        payload = {
            "event": event,
            "time_minutes": world.time_minutes,
            "time_str": minutes_to_timestr(world.time_minutes),
            "room": None,
            "student": None,
            "trigger": "console",
        }
        self.event_bus.emit("event_fired", payload)
        self.record(f"Triggered event '{event.id}'.")

    def _broadcast(self) -> None:
        self.record("Campus broadcast placeholder triggered.")

    def _first_event(self) -> Optional[Event]:
        return self.events_catalog[0] if self.events_catalog else None

    def _save_snapshot(self, world) -> None:
        save_system = getattr(world, "save_system", None)
        if not save_system:
            self.record("Save system unavailable.")
            return
        result = save_system.save(world)
        self.record(f"Saved game to {Path(result.path).name}.")

    def _load_latest(self, world) -> None:
        save_system = getattr(world, "save_system", None)
        if not save_system:
            self.record("Save system unavailable.")
            return
        path = save_system.load_latest(world)
        if path:
            self.record(f"Loaded game from {Path(path).name}.")
        else:
            self.record("No save files available.")
