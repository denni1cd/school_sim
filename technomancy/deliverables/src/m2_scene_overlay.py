"""
Reference snippet for the SceneOverlay integration shipped in Milestone M2.
"""
from __future__ import annotations

import pygame

from events.event_bus import EventBus


class OverlayExample:
    def __init__(self, base_dir: str, bus: EventBus):
        self.overlay = SceneOverlay(base_dir)
        self.bus = bus

    def attach(self, screen: pygame.Surface) -> None:
        self.overlay.attach(screen)
        self.overlay.bind(self.bus)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.overlay.handle_event(event)

    def draw(self) -> None:
        self.overlay.draw()


class SceneOverlay:
    """Subset of the production API documented for milestone traceability."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.active = False
        self.caption = None

    def attach(self, screen: pygame.Surface) -> None:
        if not pygame.font.get_init():
            pygame.font.init()
        self._screen = screen
        self._font = pygame.font.SysFont(None, 28)

    def bind(self, bus: EventBus) -> None:
        bus.subscribe("event_fired", self._on_event_fired)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.hide()

    def hide(self) -> None:
        self.active = False

    def draw(self) -> None:
        if not self.active:
            return
        overlay = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self._screen.blit(overlay, (0, 0))
        if self.caption:
            text_surface = self._font.render(self.caption, True, (255, 255, 255))
            self._screen.blit(text_surface, (20, 20))

    def _on_event_fired(self, payload: dict) -> None:
        event = payload.get("event")
        if event and getattr(event, "scene", None):
            self.caption = getattr(event.scene, "caption", "")
            self.active = True
