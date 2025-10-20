from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class ActivityEvent:
    """Structured entry for activity lifecycle changes."""

    kind: str
    timestamp: str
    npc: str
    activity: str
    room: str
    state: Dict[str, Any]


class EventLogger:
    """Collects activity lifecycle events for analysis and debugging."""

    def __init__(self) -> None:
        self._events: List[ActivityEvent] = []

    def log_activity_start(
        self,
        timestamp: str,
        *,
        npc: str,
        activity: str,
        room: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._append("activity_start", timestamp, npc=npc, activity=activity, room=room, state=state)

    def log_activity_end(
        self,
        timestamp: str,
        *,
        npc: str,
        activity: str,
        room: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._append("activity_end", timestamp, npc=npc, activity=activity, room=room, state=state)

    def log_activity_interrupt(
        self,
        timestamp: str,
        *,
        npc: str,
        activity: str,
        room: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._append("activity_interrupt", timestamp, npc=npc, activity=activity, room=room, state=state)

    def iter_events(self) -> Iterable[ActivityEvent]:
        return tuple(self._events)

    def clear(self) -> None:
        self._events.clear()

    def _append(
        self,
        kind: str,
        timestamp: str,
        *,
        npc: str,
        activity: str,
        room: str,
        state: Optional[Dict[str, Any]],
    ) -> None:
        payload = ActivityEvent(
            kind=kind,
            timestamp=timestamp,
            npc=npc,
            activity=activity,
            room=room,
            state=dict(state or {}),
        )
        self._events.append(payload)
