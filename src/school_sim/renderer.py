from pathlib import Path
from typing import Dict, List, Optional

import pygame

from .events.scene_overlay import SceneOverlay
from .principal_console import PrincipalConsole
from .room import Room
from .save_system import SaveSystem
from .student import Student

ROOM_BORDER = 2
FONT_SIZE = 16
PANEL_WIDTH = 300  # right-side debug panel
STUDENT_RADIUS = 10
CONSOLE_PADDING = 12


class Renderer:
    def __init__(
        self,
        rooms: Dict[str, Room],
        students: List[Student],
        overlay: SceneOverlay,
        console: PrincipalConsole,
        save_system: Optional[SaveSystem] = None,
    ):
        pygame.init()
        self.rooms = rooms
        self.students = students
        self.overlay = overlay
        self.console = console
        self.save_system = save_system

        max_x = max(r.x + r.width for r in rooms.values())
        max_y = max(r.y + r.height for r in rooms.values())
        win_w = int(max_x + PANEL_WIDTH + 40)
        win_h = int(max_y + 40)

        self.screen = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("School Sim Prototype")
        self.font = pygame.font.SysFont("consolas", FONT_SIZE)

        self.overlay.attach(self.screen)

    def draw(self, world_time: str):
        self.screen.fill((0, 0, 0))

        self._draw_rooms()
        self._draw_students()
        self._draw_sidebar(world_time)

        if self.console.visible:
            self._draw_console_panel(world_time)

        self.overlay.draw()
        pygame.display.flip()

    def process_events(self, world) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.overlay.handle_event(event)
                if event.key == pygame.K_p:
                    self.console.toggle()
                elif self.console.visible and event.key in (pygame.K_t, pygame.K_e, pygame.K_b):
                    self.console.handle_key(event.key, world)
                elif event.key == pygame.K_s and self.save_system:
                    result = self.save_system.save(world)
                    if self.console:
                        self.console.record(f"Saved game to {result.path.name}.")
                elif event.key == pygame.K_l and self.save_system:
                    path = self.save_system.load_latest(world)
                    if self.console:
                        if path:
                            self.console.record(f"Loaded game from {Path(path).name}.")
                        else:
                            self.console.record("No save files available.")
        return True

    def _draw_rooms(self) -> None:
        for room in self.rooms.values():
            rect = pygame.Rect(room.x, room.y, room.width, room.height)
            color = {
                "classroom": (60, 60, 200),
                "cafeteria": (200, 180, 60),
                "dorm": (120, 60, 160),
                "lounge": (60, 160, 120),
                "bathroom": (160, 160, 200),
            }.get(room.room_type, (100, 100, 100))
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, ROOM_BORDER)
            label = self.font.render(room.name, True, (255, 255, 255))
            self.screen.blit(label, (room.x + 4, room.y + 4))

    def _draw_students(self) -> None:
        for student in self.students:
            x = int(student.x)
            y = int(student.y)
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), STUDENT_RADIUS)
            name_text = self.font.render(student.name, True, (255, 255, 255))
            self.screen.blit(name_text, (x + STUDENT_RADIUS + 2, y - 8))

    def _draw_sidebar(self, world_time: str) -> None:
        panel_x = max(r.x + r.width for r in self.rooms.values()) + 20
        y = 20
        time_text = self.font.render(f"Time: {world_time}", True, (255, 255, 255))
        self.screen.blit(time_text, (panel_x, y))
        y += FONT_SIZE + 6

        for student in self.students:
            header = self.font.render(f"{student.name} ({student.current_room})", True, (200, 200, 255))
            self.screen.blit(header, (panel_x, y))
            y += FONT_SIZE
            target_text = self.font.render(f"target: {student.target_room or '-'}", True, (180, 180, 220))
            self.screen.blit(target_text, (panel_x + 10, y))
            y += FONT_SIZE
            for key in ["hunger", "energy", "stress", "discipline_risk"]:
                value = student.stats["discipline_risk"] if key == "discipline_risk" else student.needs[key]
                line = self.font.render(f"{key}: {value:.1f}", True, (220, 220, 220))
                self.screen.blit(line, (panel_x + 10, y))
                y += FONT_SIZE
            y += FONT_SIZE

    def _draw_console_panel(self, world_time: str) -> None:
        panel_width = PANEL_WIDTH - 20
        panel_height = 200
        panel_x = max(r.x + r.width for r in self.rooms.values()) + 10
        panel_y = self.screen.get_height() - panel_height - 20
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(self.screen, (30, 30, 30), panel_rect)
        pygame.draw.rect(self.screen, (200, 200, 200), panel_rect, 2)

        y = panel_y + CONSOLE_PADDING
        title = self.font.render("Principal Console", True, (255, 255, 0))
        self.screen.blit(title, (panel_x + CONSOLE_PADDING, y))
        y += FONT_SIZE + 4
        instructions = [
            "P: toggle console",
            "T: advance +15 min",
            "E: trigger first event",
            "B: campus broadcast",
            f"Time: {world_time}",
        ]
        for line in instructions:
            text = self.font.render(line, True, (220, 220, 220))
            self.screen.blit(text, (panel_x + CONSOLE_PADDING, y))
            y += FONT_SIZE

        if self.console.log:
            y += FONT_SIZE // 2
            log_title = self.font.render("Activity Log:", True, (180, 180, 180))
            self.screen.blit(log_title, (panel_x + CONSOLE_PADDING, y))
            y += FONT_SIZE
            for entry in list(self.console.log):
                text = self.font.render(f"- {entry}", True, (200, 200, 200))
                self.screen.blit(text, (panel_x + CONSOLE_PADDING, y))
                y += FONT_SIZE
