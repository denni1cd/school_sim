"""Rendering helpers for rooms, students, overlays, and the Office modal."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import pygame

from .events.scene_overlay import SceneOverlay
from .office import OfficeScreen
from .principal_console import PrincipalConsole
from .room import Room
from .save_system import SaveSystem
from .student import Student

ROOM_BORDER = 2
FONT_SIZE = 16
PANEL_WIDTH = 300  # right-side debug panel
STUDENT_RADIUS = 10
CONSOLE_PADDING = 12
OFFICE_PANEL_WIDTH = 520
OFFICE_PANEL_HEIGHT = 360
TAB_SPACING = 14
MODAL_PADDING = 18


class Renderer:
    """Render rooms, students, HUD, overlays, and the Office modal."""
    def __init__(
        self,
        rooms: Dict[str, Room],
        students: List[Student],
        overlay: SceneOverlay,
        console: PrincipalConsole,
        office: Optional[OfficeScreen] = None,
        save_system: Optional[SaveSystem] = None,
    ):
        """Initialise renderer state, Pygame display, and fonts."""
        pygame.init()
        self.rooms = rooms
        self.students = students
        self.overlay = overlay
        self.console = console
        self.office = office
        self.save_system = save_system
        self._last_hud_metrics = {"time": "08:00", "rating": 0.0, "budget": 0, "delta": 0.0, "flash": False}

        max_x = max(r.x + r.width for r in rooms.values())
        max_y = max(r.y + r.height for r in rooms.values())
        win_w = int(max_x + PANEL_WIDTH + 40)
        win_h = int(max_y + 40)

        self.screen = pygame.display.set_mode((win_w, win_h))
        pygame.display.set_caption("School Sim Prototype")
        self.font = pygame.font.SysFont("consolas", FONT_SIZE)

        self.overlay.attach(self.screen)

    def draw(self, snapshot: dict):
        """Draw the current frame (rooms, students, HUD, overlays)."""
        world_time = snapshot["time"]
        self.screen.fill((0, 0, 0))

        self._draw_rooms()
        self._draw_students()
        self._draw_sidebar(snapshot)

        if self.console.visible:
            self._draw_console_panel(snapshot)

        self.overlay.draw()
        self._draw_office_modal(snapshot)
        pygame.display.flip()

    def process_events(self, world) -> bool:
        """Process pygame events and route key presses to overlays/console."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.overlay.handle_event(event)
                if self._process_office_event(event, world):
                    continue
                if event.key == pygame.K_p:
                    self.console.toggle()
                elif self.console.visible and event.key in (pygame.K_t, pygame.K_e, pygame.K_b, pygame.K_s, pygame.K_l):
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

    def _draw_sidebar(self, snapshot: dict) -> None:
        panel_x = max(r.x + r.width for r in self.rooms.values()) + 20
        y = 20
        rating = float(snapshot.get("rating", 0.0))
        rating_delta = float(snapshot.get("rating_delta", 0.0))
        rating_flash = bool(snapshot.get("rating_flash", False))
        budget = int(snapshot.get("budget", 0))
        self._last_hud_metrics = {
            "time": snapshot["time"],
            "rating": rating,
            "budget": budget,
            "delta": rating_delta,
            "flash": rating_flash,
        }

        time_text = self.font.render(f"Time: {snapshot['time']}", True, (255, 255, 255))
        self.screen.blit(time_text, (panel_x, y))
        y += FONT_SIZE + 6
        rating_color = (255, 220, 120) if rating_flash else (200, 255, 200)
        rating_text = self.font.render(f"Rating: {rating:.1f}", True, rating_color)
        self.screen.blit(rating_text, (panel_x, y))
        y += FONT_SIZE + 4
        if abs(rating_delta) > 0.0:
            delta_text = self.font.render(f"Delta: {rating_delta:+.1f}", True, rating_color)
            self.screen.blit(delta_text, (panel_x, y))
            y += FONT_SIZE + 4
        budget_text = self.font.render(f"Budget: {budget}", True, (200, 220, 255))
        self.screen.blit(budget_text, (panel_x, y))
        y += FONT_SIZE + 10

        breakdown = snapshot.get("rating_breakdown") or {}
        if breakdown:
            header = self.font.render("Rating breakdown:", True, (210, 210, 230))
            self.screen.blit(header, (panel_x, y))
            y += FONT_SIZE
            for key, label in (("needs", "Needs"), ("compliance", "Compliance"), ("clubs", "Clubs"), ("attendance", "Attendance")):
                value = breakdown.get(key, 0.0)
                line = self.font.render(f"  {label}: {value:.1f}", True, (200, 200, 220))
                self.screen.blit(line, (panel_x, y))
                y += FONT_SIZE
            y += FONT_SIZE // 2
        history = snapshot.get("economy_history") or []
        if history:
            history_header = self.font.render("Transactions:", True, (210, 210, 230))
            self.screen.blit(history_header, (panel_x, y))
            y += FONT_SIZE
            for entry in reversed(history[-2:]):
                summary = self.font.render(
                    f"  {entry.get('time', '--:--')} {int(entry.get('delta', 0)):+} -> {int(entry.get('balance', 0))}",
                    True,
                    (200, 200, 220),
                )
                self.screen.blit(summary, (panel_x, y))
                y += FONT_SIZE
                reason = entry.get("reason")
                if reason:
                    reason_surface = self.font.render(f"    {reason}", True, (170, 170, 200))
                    self.screen.blit(reason_surface, (panel_x, y))
                    y += FONT_SIZE
            y += FONT_SIZE // 2

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

    def _draw_console_panel(self, snapshot: dict) -> None:
        world_time = snapshot["time"]
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

    def _process_office_event(self, event: pygame.event.Event, world) -> bool:
        if not self.office:
            return False
        key = event.key
        if key == pygame.K_o:
            self.office.toggle()
            if self.office.visible and hasattr(self.office, "bind_world"):
                self.office.bind_world(world)
            return True
        if not self.office.visible:
            return False
        if key == pygame.K_ESCAPE:
            self.office.close()
            return True
        if key == pygame.K_UP:
            self.office.focus_policy_option(-1)
            return True
        if key == pygame.K_DOWN:
            self.office.focus_policy_option(1)
            return True
        if key == pygame.K_LEFT:
            self.office.previous_tab()
            return True
        if key == pygame.K_RIGHT:
            self.office.next_tab()
            return True
        if key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
            index = key - pygame.K_1
            self.office.select_tab(index)
            return True
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            result = self.office.activate(world)
            if result:
                if result.message and self.console:
                    self.console.record(result.message)
                if result.overlay_caption and self.overlay:
                    self.overlay.show(None, result.overlay_caption)
            return True
        return True  # swallow other keys while office modal is open

    def _draw_office_modal(self, snapshot: dict) -> None:
        if not self.office or not self.office.visible:
            return
        width, height = self.screen.get_size()
        dim_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 180))
        self.screen.blit(dim_surface, (0, 0))

        panel_w = min(OFFICE_PANEL_WIDTH, width - 2 * MODAL_PADDING)
        panel_h = min(OFFICE_PANEL_HEIGHT, height - 2 * MODAL_PADDING)
        panel_rect = pygame.Rect(
            (width - panel_w) // 2,
            (height - panel_h) // 2,
            panel_w,
            panel_h,
        )
        pygame.draw.rect(self.screen, (25, 25, 25), panel_rect)
        pygame.draw.rect(self.screen, (210, 210, 230), panel_rect, 2)

        view = self.office.get_active_view(snapshot)
        tab_titles = self.office.tab_titles()

        tabs_y = panel_rect.top + MODAL_PADDING
        tab_x = panel_rect.left + MODAL_PADDING
        for idx, title in enumerate(tab_titles):
            active = idx == self.office.active_index
            display = f"[{title}]" if active else title
            color = (255, 255, 160) if active else (200, 200, 200)
            label = self.font.render(display, True, color)
            self.screen.blit(label, (tab_x, tabs_y))
            tab_x += label.get_width() + TAB_SPACING

        title_text = self.font.render(f"Headmistress Office - {view.title}", True, (255, 255, 255))
        self.screen.blit(title_text, (panel_rect.left + MODAL_PADDING, tabs_y + FONT_SIZE + 6))

        body_y = tabs_y + FONT_SIZE * 2 + 14
        body_x = panel_rect.left + MODAL_PADDING
        max_body_width = panel_rect.width - MODAL_PADDING * 2
        for line in view.lines:
            text = self._render_wrapped(line, max_body_width)
            for surface in text:
                self.screen.blit(surface, (body_x, body_y))
                body_y += FONT_SIZE + 2
        footer_y = panel_rect.bottom - MODAL_PADDING - FONT_SIZE * 2
        helpers = [
            "Left/Right or 1-5 to switch tabs",
            "Enter to apply selection, Esc to close",
        ]
        for helper in helpers:
            helper_surface = self.font.render(helper, True, (180, 180, 190))
            self.screen.blit(helper_surface, (panel_rect.left + MODAL_PADDING, footer_y))
            footer_y += FONT_SIZE

    def _render_wrapped(self, text: str, max_width: int) -> List[pygame.Surface]:
        """Render a line with basic wrapping against the modal width."""
        if not text:
            return [self.font.render("", True, (220, 220, 220))]
        words = text.split()
        surfaces: List[pygame.Surface] = []
        current = ""
        for word in words:
            tentative = f"{current} {word}".strip()
            surface = self.font.render(tentative, True, (220, 220, 220))
            if surface.get_width() > max_width and current:
                surfaces.append(self.font.render(current, True, (220, 220, 220)))
                current = word
            else:
                current = tentative
        if current or not surfaces:
            surfaces.append(self.font.render(current, True, (220, 220, 220)))
        return surfaces

