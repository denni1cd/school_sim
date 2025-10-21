from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ActivityState:
    """Snapshot describing an activity's public-facing state."""

    label: str
    status: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def with_update(self, **changes: Any) -> "ActivityState":
        updated = ActivityState(label=self.label, status=self.status, metadata=dict(self.metadata))
        updated.metadata.update(changes)
        return updated


class Activity(ABC):
    """Base class for concrete NPC activities."""

    def __init__(
        self,
        *,
        name: str,
        label: str,
        interaction_key: str,
        room_id: str,
        duration: int,
        state_defaults: Optional[Dict[str, Any]] = None,
        overrides: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.label = label
        self.interaction_key = interaction_key
        self.room_id = room_id
        self.duration = duration
        self.remaining = duration
        metadata = dict(state_defaults or {})
        if overrides:
            metadata.update(overrides)
        self.state = ActivityState(label=label, status="pending", metadata=metadata)

    @abstractmethod
    def on_start(self) -> ActivityState:
        """Return the initial state when the activity begins."""

    def on_interrupt(self, reason: str | None = None) -> ActivityState:
        self.state.status = "interrupted"
        if reason:
            self.state.metadata["reason"] = reason
        return self.state

    def on_complete(self) -> ActivityState:
        self.state.status = "complete"
        return self.state

    def tick(self, minutes: int = 1) -> Optional[ActivityState]:
        if self.remaining > 0:
            self.remaining = max(0, self.remaining - minutes)
        return None


class PassiveActivity(Activity):
    """Simple activity that only changes status during lifecycle events."""

    def on_start(self) -> ActivityState:
        self.state.status = "active"
        return self.state


class GradualActivity(Activity):
    """Activity that exposes progress percentage as it advances."""

    def on_start(self) -> ActivityState:
        self.state.status = "active"
        if self.duration:
            self.state.metadata["progress"] = 0.0
        return self.state

    def tick(self, minutes: int = 1) -> Optional[ActivityState]:
        changed = super().tick(minutes)
        if self.duration:
            elapsed = self.duration - self.remaining
            progress = min(1.0, max(0.0, elapsed / self.duration))
            prev = self.state.metadata.get("progress")
            if prev != progress:
                self.state.metadata["progress"] = progress
                changed = self.state
        return changed
