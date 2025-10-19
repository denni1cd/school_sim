from __future__ import annotations

import argparse
import sys
from math import hypot
from pathlib import Path
from typing import Optional

import pygame

from .actors.pc import Player
from .config import load_config
from .core.map import MapGrid
from .simulation import Simulation, resolve_data_path
from .systems.player_controller import InputState, PlayerController

ROOT = Path(__file__).resolve().parents[1]

WALKABLE_COLOR = (60, 80, 120)
WALL_COLOR = (25, 30, 40)
GRID_COLOR = (40, 50, 70)
ROOM_OUTLINE = (180, 200, 255)
PLAYER_COLOR = (240, 210, 90)
NPC_COLOR = (150, 200, 120)
DOOR_COLOR = (255, 180, 90)
TEXT_COLOR = (235, 235, 235)
BACKGROUND = (10, 12, 18)


def _nearest_npc(player: Player, simulation: Simulation):
    px, py = player.position
    closest = None
    best_dist = float('inf')
    for npc in simulation.npcs:
        nx, ny = npc.x + 0.5, npc.y + 0.5
        dist = hypot(px - nx, py - ny)
        if dist < best_dist:
            closest = npc
            best_dist = dist
    return closest, best_dist


def _draw_map(surface, grid: MapGrid, player: Player, simulation: Simulation, font, prompt: Optional[str], message: Optional[str]) -> None:
    tile_size = grid.tile_size
    surface.fill(BACKGROUND)

    for y in range(grid.height):
        for x in range(grid.width):
            rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
            color = WALKABLE_COLOR if grid.passability[y][x] else WALL_COLOR
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, GRID_COLOR, rect, width=1)

    for room in grid.rooms.values():
        rx, ry, rw, rh = room.rect
        rect = pygame.Rect(rx * tile_size, ry * tile_size, rw * tile_size, rh * tile_size)
        pygame.draw.rect(surface, ROOM_OUTLINE, rect, width=2)
        label = font.render(room.name, True, TEXT_COLOR)
        surface.blit(label, (rect.x + 6, rect.y + 6))
        for door_x, door_y in room.doors:
            door_rect = pygame.Rect(door_x * tile_size, door_y * tile_size, tile_size, tile_size)
            door_rect.inflate_ip(-tile_size * 0.5, -tile_size * 0.5)
            pygame.draw.rect(surface, DOOR_COLOR, door_rect, border_radius=3)

    px, py = player.position
    player_marker = pygame.Rect(0, 0, tile_size * 0.5, tile_size * 0.5)
    player_marker.center = (px * tile_size, py * tile_size)
    pygame.draw.rect(surface, PLAYER_COLOR, player_marker, border_radius=6)

    for npc in simulation.npcs:
        marker = pygame.Rect(0, 0, tile_size * 0.5, tile_size * 0.5)
        marker.center = ((npc.x + 0.5) * tile_size, (npc.y + 0.5) * tile_size)
        pygame.draw.rect(surface, NPC_COLOR, marker, border_radius=6)
        label = font.render(f"{npc.name} ({npc.state.value})", True, TEXT_COLOR)
        surface.blit(label, (marker.x, marker.y - 18))

    info_lines = [
        f"Time: {simulation.clock.get_time_str()}",
        "Controls: WASD / Arrow Keys",
        "Esc to exit, E to interact",
    ]
    if prompt:
        info_lines.append(prompt)
    for idx, line in enumerate(info_lines):
        text_surface = font.render(line, True, TEXT_COLOR)
        surface.blit(text_surface, (16, 16 + idx * 22))

    if message:
        overlay = font.render(message, True, TEXT_COLOR)
        surface.blit(overlay, (16, surface.get_height() - 32))


def run(profile: str | None = None) -> None:
    cfg = load_config(profile=profile)

    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('School Simulation Prototype - Milestone 7')

    data_cfg = cfg.get('data', {})
    map_path = resolve_data_path(data_cfg.get('map_file', 'data/campus_map.json'))
    grid = MapGrid(str(map_path))
    tile_size = grid.tile_size
    window_width = max(cfg['window']['width'], grid.width * tile_size)
    window_height = max(cfg['window']['height'], grid.height * tile_size)
    surface = pygame.display.set_mode((window_width, window_height))
    font = pygame.font.SysFont('consolas', 18)

    player = Player(x=2, y=2)
    controller = PlayerController(grid, cfg['movement']['pc_speed_tiles_per_sec'])
    simulation = Simulation(cfg, grid)
    tick_rate = float(cfg['time']['tick_rate_hz'])
    tick_accumulator = 0.0

    message_text: Optional[str] = None
    message_timer = 0.0

    clock = pygame.time.Clock()
    running = True
    while running:
        delta_seconds = clock.tick(cfg['time']['tick_rate_hz']) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_e:
                    npc, dist = _nearest_npc(player, simulation)
                    if npc and dist <= 1.5:
                        message_text = simulation.interact_with(npc)
                        message_timer = 3.0

        keys = pygame.key.get_pressed()
        input_state = InputState.from_axes(
            left=keys[pygame.K_a] or keys[pygame.K_LEFT],
            right=keys[pygame.K_d] or keys[pygame.K_RIGHT],
            up=keys[pygame.K_w] or keys[pygame.K_UP],
            down=keys[pygame.K_s] or keys[pygame.K_DOWN],
        )
        controller.update(player, input_state, delta_seconds)

        tick_accumulator += delta_seconds * tick_rate
        while tick_accumulator >= 1.0:
            simulation.tick()
            tick_accumulator -= 1.0

        if message_timer > 0.0:
            message_timer -= delta_seconds
            if message_timer <= 0.0:
                message_text = None

        npc, dist = _nearest_npc(player, simulation)
        prompt = None
        if npc and dist <= 1.5:
            prompt = f"Press E to chat with {npc.name}"

        _draw_map(surface, grid, player, simulation, font, prompt, message_text)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the pygame school simulation viewer.')
    parser.add_argument('--profile', type=str, help='Configuration profile to load (overrides settings.yaml).')
    args = parser.parse_args()
    try:
        run(profile=args.profile)
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit(0)
