"""Condition evaluation and event dispatch helpers for school events."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from ..timetable import minutes_to_timestr
from .event_bus import EventBus
from .event_models import Event


@dataclass(frozen=True)
class _NeedComparator:
    """Compare a single need value against configured thresholds."""

    need: str
    op: str
    threshold: float

    def evaluate(self, student) -> bool:
        """Compare the requested need value against the threshold."""
        value = float(student.needs.get(self.need, 0.0))
        if self.op == ">=":
            return value >= self.threshold
        if self.op == ">":
            return value > self.threshold
        if self.op == "<=":
            return value <= self.threshold
        if self.op == "<":
            return value < self.threshold
        if self.op == "==":
            return value == self.threshold
        raise ValueError(f"Unsupported operator '{self.op}'.")


@dataclass(frozen=True)
class _StudentInComparator:
    """Evaluate whether a student belongs to a specific homeroom."""

    homeroom: str

    def evaluate(self, student) -> bool:
        """Return True when the student is assigned to the expected homeroom."""
        return getattr(student, "homeroom", None) == self.homeroom


class ConditionEvaluator:
    """Evaluate the simple condition language defined in the specification.

    Supports `needs.<name> comparison value`, `student in <homeroom>`, and
    boolean `and`/`or`.
    """

    def __init__(self, condition: str):
        """Parse and store terms for the submitted condition string."""
        self._terms = self._parse(condition)

    def evaluate(self, world) -> bool:
        """Return True if any set of terms matches a student in the world."""
        if not self._terms:
            return True
        for and_group in self._terms:
            if self._evaluate_and_group(and_group, world):
                return True
        return False

    def _evaluate_and_group(self, group: List[Callable], world) -> bool:
        """Check whether at least one student satisfies every predicate."""
        for student in world.students:
            if all(predicate(student) for predicate in group):
                return True
        return False

    @staticmethod
    def _parse(condition: str) -> List[List[Callable]]:
        """Tokenize and group condition clauses for evaluation."""
        tokens = _tokenize(condition)
        if not tokens:
            return []

        groups: List[List[Callable]] = []
        current: List[Callable] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.lower() == "and":
                i += 1
                continue
            if token.lower() == "or":
                if current:
                    groups.append(current)
                    current = []
                i += 1
                continue
            if token.lower() == "student":
                if i + 2 >= len(tokens) or tokens[i + 1].lower() != "in":
                    raise ValueError("Invalid 'student in' expression.")
                comparator = _StudentInComparator(homeroom=tokens[i + 2])
                current.append(lambda student, cmp=comparator: cmp.evaluate(student))
                i += 3
                continue
            if token.lower().startswith("needs."):
                if i + 2 >= len(tokens):
                    raise ValueError("Incomplete needs comparison expression.")
                need = token.split(".", 1)[1]
                comparator = _NeedComparator(
                    need=need,
                    op=tokens[i + 1],
                    threshold=float(tokens[i + 2]),
                )
                current.append(lambda student, cmp=comparator: cmp.evaluate(student))
                i += 3
                continue
            raise ValueError(f"Unsupported token '{token}' in condition.")

        if current:
            groups.append(current)
        return groups


def _tokenize(condition: str) -> List[str]:
    """Split the condition string into tokens understood by the evaluator."""
    pattern = r"(?:needs\.\w+|>=|<=|==|>|<|and|or|student|in|[A-Za-z0-9_\.]+)"
    return re.findall(pattern, condition, flags=re.IGNORECASE)


class EventRules:
    """Wire configured events to the bus and fire them when conditions match."""

    def __init__(self, events: List[Event], bus: EventBus):
        """Prepare event bindings and subscribe to world time/room notifications."""
        self.events = events
        self.bus = bus
        self.world = None
        self._fired_once: set[str] = set()
        self._last_fired_at: Dict[str, int] = {}
        self._compiled: Dict[str, Optional[ConditionEvaluator]] = {
            event.id: ConditionEvaluator(event.condition) if event.condition else None
            for event in events
        }
        self.bus.subscribe("time_tick", self._on_time_tick)
        self.bus.subscribe("room_enter", self._on_room_event)

    def bind_world(self, world) -> None:
        """Associate the rules engine with the active World instance."""
        self.world = world

    def _on_time_tick(self, payload: dict) -> None:
        """Handle time tick messages to re-evaluate events at the current time."""
        if not self.world:
            return
        time_minutes = payload["time_minutes"]
        time_str = payload["time_str"]
        self._evaluate_events(time_minutes, time_str=time_str)

    def _on_room_event(self, payload: dict) -> None:
        """Handle room-enter notifications to potentially trigger room-specific events."""
        if not self.world:
            return
        time_minutes = self.world.time_minutes
        room_name = payload.get("room")
        student = payload.get("student")
        self._evaluate_events(time_minutes, room_name=room_name, student=student)

    def _evaluate_events(
        self,
        time_minutes: int,
        *,
        time_str: Optional[str] = None,
        room_name: Optional[str] = None,
        student=None,
    ) -> None:
        """Iterate through configured events and fire those whose conditions match."""
        time_str = time_str or minutes_to_timestr(time_minutes)
        for event in self.events:
            if event.once and event.id in self._fired_once:
                continue
            if event.when and event.when != time_str:
                continue
            if event.room and not self._room_match(event.room, room_name):
                continue
            evaluator = self._compiled[event.id]
            if evaluator and not evaluator.evaluate(self.world):
                continue
            if self._last_fired_at.get(event.id) == time_minutes:
                continue
            self._fire_event(event, time_minutes, time_str, room_name, student)

    def _room_match(self, expected_room: str, active_room: Optional[str]) -> bool:
        """Return True when the active room matches the configured room filter."""
        if active_room:
            return expected_room == active_room
        return any(s.current_room == expected_room for s in self.world.students)

    def _fire_event(
        self,
        event: Event,
        time_minutes: int,
        time_str: str,
        room_name: Optional[str],
        student,
    ) -> None:
        """Emit the event payload and track when it last fired."""
        payload = {
            "event": event,
            "time_minutes": time_minutes,
            "time_str": time_str,
            "room": room_name,
            "student": student,
        }
        self.bus.emit("event_fired", payload)
        self._last_fired_at[event.id] = time_minutes
        if event.once:
            self._fired_once.add(event.id)
