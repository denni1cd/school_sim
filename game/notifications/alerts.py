from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

from ..simulation.schedule_generator import format_minutes


@dataclass(slots=True)
class Alert:
    """Represents an incident requiring principal attention."""

    id: str
    category: str
    severity: str
    message: str
    room_id: Optional[str]
    npc_ids: Tuple[str, ...]
    created_at: str
    acknowledged_at: Optional[str] = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def acknowledged(self) -> bool:
        return self.acknowledged_at is not None


class AlertBus:
    """Simple pub/sub channel for simulation alerts with cooldown support."""

    def __init__(self, *, cooldown_minutes: int = 10) -> None:
        self._cooldown_minutes = max(0, cooldown_minutes)
        self._alerts: MutableMapping[str, Alert] = {}
        self._subscribers: List[Callable[[Alert], None]] = []
        self._cooldowns: Dict[Tuple[str, Optional[str], Tuple[str, ...]], int] = {}
        self._history: List[str] = []

    def subscribe(self, callback: Callable[[Alert], None]) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Alert], None]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def publish(
        self,
        category: str,
        *,
        minute_stamp: int,
        severity: str,
        message: str,
        room_id: Optional[str] = None,
        npc_ids: Sequence[str] | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> Alert:
        """Create and broadcast an alert, respecting cooldown windows."""

        normalized_npc_ids = tuple(sorted(npc_ids or ()))
        cooldown_key = (category, room_id, normalized_npc_ids)
        last_minute = self._cooldowns.get(cooldown_key)
        if last_minute is not None and minute_stamp - last_minute < self._cooldown_minutes:
            existing_id = next(
                (
                    alert_id
                    for alert_id in reversed(self._history)
                    if self._alerts[alert_id].category == category
                    and self._alerts[alert_id].room_id == room_id
                    and self._alerts[alert_id].npc_ids == normalized_npc_ids
                ),
                None,
            )
            if existing_id is not None:
                return self._alerts[existing_id]
        alert_id = str(uuid.uuid4())
        alert = Alert(
            id=alert_id,
            category=category,
            severity=severity,
            message=message,
            room_id=room_id,
            npc_ids=normalized_npc_ids,
            created_at=format_minutes(minute_stamp),
            metadata=dict(metadata or {}),
        )
        self._alerts[alert_id] = alert
        self._history.append(alert_id)
        self._cooldowns[cooldown_key] = minute_stamp
        for subscriber in tuple(self._subscribers):
            subscriber(alert)
        return alert

    def acknowledge(self, alert_id: str, *, minute_stamp: Optional[int] = None) -> Alert:
        alert = self._alerts[alert_id]
        if alert.acknowledged_at is None:
            alert.acknowledged_at = (
                format_minutes(minute_stamp) if minute_stamp is not None else alert.created_at
            )
            for subscriber in tuple(self._subscribers):
                subscriber(alert)
        return alert

    def active_alerts(self) -> List[Alert]:
        return [self._alerts[alert_id] for alert_id in self._history if not self._alerts[alert_id].acknowledged()]

    def iter_history(self) -> Iterable[Alert]:
        for alert_id in self._history:
            yield self._alerts[alert_id]

    def latest_by_category(self, category: str) -> Optional[Alert]:
        for alert_id in reversed(self._history):
            alert = self._alerts[alert_id]
            if alert.category == category:
                return alert
        return None

    def clear(self) -> None:
        self._alerts.clear()
        self._history.clear()
        self._cooldowns.clear()

