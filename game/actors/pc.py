from __future__ import annotations

import math

from .base_actor import Actor


class Player(Actor):
    """Player-controlled actor with floating-point position tracking."""

    def __init__(self, name: str = 'PC', x: int = 2, y: int = 2):
        super().__init__(name, int(x), int(y))
        self._fx = float(x) + 0.5
        self._fy = float(y) + 0.5
        self._sync_tile()

    @property
    def position(self) -> tuple[float, float]:
        return self._fx, self._fy

    def move_to(self, *, fx: float | None = None, fy: float | None = None) -> None:
        if fx is not None:
            self._fx = fx
        if fy is not None:
            self._fy = fy
        self._sync_tile()

    def teleport_to_tile(self, tile_x: int, tile_y: int) -> None:
        self._fx = float(tile_x) + 0.5
        self._fy = float(tile_y) + 0.5
        self._sync_tile()

    def _sync_tile(self) -> None:
        self.x = int(math.floor(self._fx))
        self.y = int(math.floor(self._fy))


