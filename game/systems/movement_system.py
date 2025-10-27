from __future__ import annotations

from collections import OrderedDict
from typing import Set, Tuple

from ..actors.base_actor import NPCState
from ..core.pathfinding import astar


class MovementSystem:
    def __init__(self, grid, *, cache_size: int = 128):
        self.grid = grid
        self._path_cache: "OrderedDict[Tuple[Tuple[int, int], Tuple[int, int]], Tuple[Tuple[int, int], ...]]" = (
            OrderedDict()
        )
        self._cache_size = max(0, cache_size)

    def _cache_key(self, start: Tuple[int, int], target: Tuple[int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (start, target)

    def _get_cached_path(
        self, start: Tuple[int, int], target: Tuple[int, int]
    ) -> Tuple[Tuple[int, int], ...] | None:
        if not self._path_cache:
            return None
        key = self._cache_key(start, target)
        path = self._path_cache.get(key)
        if path is not None:
            # Promote the entry for simple LRU behaviour.
            self._path_cache.move_to_end(key)
        return path

    def _store_cached_path(self, start: Tuple[int, int], target: Tuple[int, int], path: Tuple[Tuple[int, int], ...]) -> None:
        if self._cache_size <= 0:
            return
        key = self._cache_key(start, target)
        self._path_cache[key] = path
        self._path_cache.move_to_end(key)
        while len(self._path_cache) > self._cache_size:
            self._path_cache.popitem(last=False)

    def plan_if_needed(self, actor, blocked: Set[Tuple[int, int]] | None = None) -> None:
        if actor.target is None or (actor.x, actor.y) == actor.target:
            return
        if not actor.path:
            start = (actor.x, actor.y)
            target = actor.target
            cached = None
            if not blocked:
                cached = self._get_cached_path(start, target)
            if cached is None:
                path = astar(self.grid, start, target, blocked=blocked)
                if not path:
                    actor.target = None
                    actor.state = NPCState.IDLE
                    return
                if not blocked:
                    self._store_cached_path(start, target, tuple(path))
            else:
                path = list(cached)
            if not path:
                actor.target = None
                actor.state = NPCState.IDLE
                return
            actor.path = list(path[1:]) if len(path) > 1 else []
        if actor.path:
            actor.state = NPCState.MOVING

    def step(self, actor, occupied: Set[Tuple[int, int]] | None = None, steps: int = 1) -> bool:
        if occupied is None:
            occupied = set()
        reached = False
        while steps > 0 and actor.path:
            nx, ny = actor.path[0]
            if (nx, ny) in occupied:
                break
            actor.path.pop(0)
            occupied.add((nx, ny))
            actor.x, actor.y = nx, ny
            steps -= 1
        if not actor.path and actor.target is not None and (actor.x, actor.y) == actor.target:
            actor.target = None
            actor.state = NPCState.IDLE
            reached = True
        return reached