"""
Reference implementation notes for the Milestone M2 event system.

This mirrors the production modules under `events/`:
  - `event_models.py` with dataclasses and validation.
  - `event_loader.py` for YAML ingestion.
  - `event_rules.py` subscribing to the EventBus.
  - `event_bus.py` retaining the publish/subscribe primitive.
"""
from __future__ import annotations

from events.event_bus import EventBus
from events.event_loader import load_events
from events.event_rules import EventRules


def bootstrap_event_system(events_path: str = "configs/events.yaml") -> tuple[list, EventBus, EventRules]:
    """
    Demonstrates the wiring sequence used in production:

    1. Load events from YAML and validate them.
    2. Instantiate a shared EventBus.
    3. Create EventRules bound to the bus so time ticks and room enters trigger events.
    """
    events = load_events(events_path)
    bus = EventBus()
    rules = EventRules(events, bus)
    return events, bus, rules


def attach_world(world, bus: EventBus, rules: EventRules) -> None:
    """
    Bind a World instance to the rules and reuse the bus inside the world so
    that `time_tick`, `room_enter`, and `needs_update` messages flow correctly.
    """
    world.event_bus = bus
    rules.bind_world(world)
