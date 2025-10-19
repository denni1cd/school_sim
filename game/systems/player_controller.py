from __future__ import annotations

import math
from dataclasses import dataclass

from ..actors.pc import Player
from ..core.map import MapGrid


@dataclass(frozen=True)
class InputState:
    horizontal: float = 0.0
    vertical: float = 0.0

    @staticmethod
    def from_axes(left: bool, right: bool, up: bool, down: bool) -> "InputState":
        dx = (1.0 if right else 0.0) - (1.0 if left else 0.0)
        dy = (1.0 if down else 0.0) - (1.0 if up else 0.0)
        return InputState(horizontal=dx, vertical=dy)


class PlayerController:
    def __init__(self, grid: MapGrid, speed_tiles_per_second: float):
        self._grid = grid
        self._speed = speed_tiles_per_second

    def update(self, player: Player, input_state: InputState, delta_seconds: float) -> None:
        if delta_seconds <= 0:
            return

        dx, dy = input_state.horizontal, input_state.vertical
        length = math.hypot(dx, dy)
        if length > 1.0:
            dx /= length
            dy /= length

        step = self._speed * delta_seconds
        if dx:
            self._move_axis(player, dx * step, axis=0)
        if dy:
            self._move_axis(player, dy * step, axis=1)

    def _move_axis(self, player: Player, delta: float, axis: int) -> None:
        fx, fy = player.position
        if axis == 0:
            target = fx + delta
            tile_x = math.floor(target)
            tile_y = math.floor(fy)
            if self._grid.walkable(tile_x, tile_y):
                player.move_to(fx=target)
        else:
            target = fy + delta
            tile_x = math.floor(fx)
            tile_y = math.floor(target)
            if self._grid.walkable(tile_x, tile_y):
                player.move_to(fy=target)

        # If the tile was not walkable we simply remain in place, keeping movement responsive without clipping.

