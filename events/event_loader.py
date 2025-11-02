from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

import yaml

from .event_models import Event, EventValidationError, Scene


def _ensure_iterable(payload) -> Iterable[dict]:
    if payload is None:
        return []
    if not isinstance(payload, list):
        raise EventValidationError("Events configuration must be a list of mappings.")
    return payload


def load_events(path: str) -> List[Event]:
    """
    Load events from the given YAML path and return validated Event objects.
    """
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    events: List[Event] = []
    for entry in _ensure_iterable(payload):
        if not isinstance(entry, dict):
            raise EventValidationError("Each event entry must be a mapping.")
        if "id" not in entry:
            raise EventValidationError("Event entry missing required field 'id'.")

        scene_payload = entry.get("scene")
        scene = None
        if scene_payload is not None:
            if not isinstance(scene_payload, dict):
                raise EventValidationError("Scene configuration must be a mapping.")
            scene = Scene(
                image=scene_payload.get("image"),
                caption=scene_payload.get("caption"),
            )

        event = Event(
            id=str(entry["id"]),
            when=entry.get("when"),
            room=entry.get("room"),
            condition=entry.get("condition"),
            scene=scene,
            once=bool(entry.get("once", False)),
            metadata=entry.get("metadata", {}) or {},
        )
        events.append(event)

    return events
