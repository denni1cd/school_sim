import math
from pathlib import Path

import pytest
import yaml

from game.actors.pc import Player
from game.core.map import MapGrid
from game.systems.player_controller import InputState, PlayerController

CFG = yaml.safe_load((Path('config') / 'settings.yaml').read_text())
PC_SPEED = CFG['movement']['pc_speed_tiles_per_sec']


def _make_grid() -> MapGrid:
    return MapGrid(str(Path('data') / 'campus_map.json'))


def _make_controller(grid: MapGrid) -> PlayerController:
    return PlayerController(grid, PC_SPEED)


def test_player_moves_with_input() -> None:
    grid = _make_grid()
    controller = _make_controller(grid)
    player = Player(x=2, y=2)

    start_x, start_y = player.position
    controller.update(player, InputState(horizontal=1.0, vertical=0.0), 0.5)
    new_x, new_y = player.position

    assert new_x > start_x
    assert math.isclose(new_y, start_y, rel_tol=1e-6)


def test_player_respects_map_walls() -> None:
    grid = _make_grid()
    controller = _make_controller(grid)
    player = Player(x=grid.width - 3, y=2)

    controller.update(player, InputState(horizontal=1.0, vertical=0.0), 1.0)

    tile_x = math.floor(player.position[0])
    assert tile_x == grid.width - 3


def test_diagonal_movement_is_normalized() -> None:
    grid = _make_grid()
    controller = _make_controller(grid)
    player = Player(x=2, y=2)

    start_x, start_y = player.position
    controller.update(player, InputState(horizontal=1.0, vertical=1.0), 1.0)
    end_x, end_y = player.position

    distance = math.hypot(end_x - start_x, end_y - start_y)
    assert distance == pytest.approx(PC_SPEED, rel=1e-2)
