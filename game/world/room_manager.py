from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Set

from ..core.map import MapGrid
from ..simulation.activities import Activity


@dataclass
class RoomSnapshot:
    room_id: str
    occupants: Set[str] = field(default_factory=set)
    activity_counts: Dict[str, int] = field(default_factory=dict)
    activity_state: Dict[str, Mapping[str, object]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "occupants": sorted(self.occupants),
            "activity_counts": dict(self.activity_counts),
            "activity_state": {key: dict(value) for key, value in self.activity_state.items()},
        }


class RoomManager:
    """Tracks room occupancy and active activities."""

    def __init__(self, grid: MapGrid) -> None:
        self._grid = grid
        self._occupants: MutableMapping[str, Set[str]] = defaultdict(set)
        self._activities: MutableMapping[str, Dict[str, Activity]] = defaultdict(dict)
        self._subscribers: MutableMapping[str, List[Callable[[RoomSnapshot], None]]] = defaultdict(list)

    def subscribe(self, room_id: str, callback: Callable[[RoomSnapshot], None]) -> None:
        self._subscribers[room_id].append(callback)
        callback(self.snapshot(room_id))

    def unsubscribe(self, room_id: str, callback: Callable[[RoomSnapshot], None]) -> None:
        if callback in self._subscribers.get(room_id, []):
            self._subscribers[room_id].remove(callback)

    def track_entry(self, npc_name: str, room_id: str) -> None:
        if room_id not in self._grid.rooms:
            return
        self._occupants[room_id].add(npc_name)
        self._notify(room_id)

    def track_exit(self, npc_name: str, room_id: str) -> None:
        occupants = self._occupants.get(room_id)
        if not occupants:
            return
        if npc_name in occupants:
            occupants.remove(npc_name)
            if not occupants:
                self._occupants.pop(room_id, None)
        self._activities.get(room_id, {}).pop(npc_name, None)
        self._notify(room_id)

    def start_activity(self, npc_name: str, activity: Activity) -> None:
        room_id = activity.room_id
        if room_id not in self._grid.rooms:
            return
        self._occupants[room_id].add(npc_name)
        self._activities[room_id][npc_name] = activity
        self._notify(room_id)

    def update_activity(self, npc_name: str, activity: Activity) -> None:
        room_id = activity.room_id
        if room_id not in self._grid.rooms:
            return
        if npc_name not in self._occupants.get(room_id, set()):
            self._occupants[room_id].add(npc_name)
        self._activities[room_id][npc_name] = activity
        self._notify(room_id)

    def end_activity(self, npc_name: str, activity: Activity) -> None:
        room_id = activity.room_id
        if room_id not in self._grid.rooms:
            return
        self._activities.get(room_id, {}).pop(npc_name, None)
        occupants = self._occupants.get(room_id)
        if occupants and npc_name in occupants:
            occupants.remove(npc_name)
            if not occupants:
                self._occupants.pop(room_id, None)
        self._notify(room_id)

    def snapshot(self, room_id: str) -> RoomSnapshot:
        occupants = set(self._occupants.get(room_id, set()))
        active = self._activities.get(room_id, {})
        counts: Dict[str, int] = defaultdict(int)
        state: Dict[str, Mapping[str, object]] = {}
        for npc, activity in active.items():
            counts[activity.label] += 1
            state[npc] = {
                "label": activity.label,
                "status": activity.state.status,
                "metadata": dict(activity.state.metadata),
            }
        return RoomSnapshot(room_id=room_id, occupants=occupants, activity_counts=dict(counts), activity_state=state)

    def iter_snapshots(self) -> Iterable[RoomSnapshot]:
        for room_id in sorted(self._grid.rooms):
            yield self.snapshot(room_id)

    def _notify(self, room_id: str) -> None:
        snapshot = self.snapshot(room_id)
        for callback in self._subscribers.get(room_id, []):
            callback(snapshot)
