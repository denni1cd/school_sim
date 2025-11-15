"""Event dispatch bus used by scenes and rule sets to communicate."""

from collections import defaultdict
from typing import Callable, Dict, List


class EventBus:
    """Lightweight pub/sub bus for simulation events."""

    def __init__(self):
        """Initialise the subscription registry."""
        self._subs: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, callback: Callable):
        """Register a callback to receive payloads for the given topic."""
        self._subs[topic].append(callback)

    def emit(self, topic: str, payload: dict):
        """Deliver a payload to all subscribers of a topic."""
        for cb in self._subs.get(topic, []):
            cb(payload)
