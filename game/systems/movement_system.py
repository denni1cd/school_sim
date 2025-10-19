from __future__ import annotations

from typing import Set, Tuple

from ..actors.base_actor import NPCState
from ..core.pathfinding import astar


class MovementSystem:
    def __init__(self, grid):
        self.grid = grid

    def plan_if_needed(self, actor, blocked: Set[Tuple[int, int]] | None = None) -> None:
        if actor.target is None or (actor.x, actor.y) == actor.target:
            return
        if not actor.path:
            path = astar(self.grid, (actor.x, actor.y), actor.target, blocked=blocked)
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