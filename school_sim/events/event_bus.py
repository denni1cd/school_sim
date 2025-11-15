from collections import defaultdict
from typing import Callable, Dict, List


class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, callback: Callable):
        self._subs[topic].append(callback)

    def emit(self, topic: str, payload: dict):
        for cb in self._subs.get(topic, []):
            cb(payload)
