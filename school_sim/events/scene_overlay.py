from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import pygame

from .event_bus import EventBus


@dataclass
class ScenePayload:
    image: Optional[str]
    caption: Optional[str]


class SceneOverlay:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.active = False
        self.image: Optional[pygame.Surface] = None
        self.caption: Optional[str] = None
        self._font: Optional[pygame.font.Font] = None
        self._screen: Optional[pygame.Surface] = None

    def attach(self, screen: pygame.Surface) -> None:
        self._screen = screen
        if not pygame.font.get_init():
            pygame.font.init()
        self._font = pygame.font.SysFont(None, 28)

    def bind(self, bus: EventBus) -> None:
        bus.subscribe("event_fired", self._on_event_fired)
        bus.subscribe("policy_overlay", self._on_policy_overlay)
        bus.subscribe("curriculum_overlay", self._on_curriculum_overlay)

    def handle_event(self, event: pygame.event.EventType) -> None:
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.hide()

    def show(self, image_path: Optional[str], caption: Optional[str]) -> None:
        self.caption = (caption or "").strip()
        if image_path:
            full_path = os.path.join(self.base_dir, image_path)
            try:
                self.image = pygame.image.load(full_path).convert_alpha()
            except Exception:
                self.image = None
                self.caption = f"(missing image) {self.caption}"
        else:
            self.image = None
        self.active = True

    def hide(self) -> None:
        self.active = False
        self.image = None
        self.caption = None

    @property
    def is_active(self) -> bool:
        return self.active

    def draw(self) -> None:
        if not self.active or self._screen is None:
            return
        overlay = pygame.Surface(self._screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self._screen.blit(overlay, (0, 0))

        if self.image:
            rect = self.image.get_rect(center=self._screen.get_rect().center)
            self._screen.blit(self.image, rect)

        if self.caption and self._font:
            text_surface = self._font.render(self.caption, True, (255, 255, 255))
            padding = 20
            self._screen.blit(text_surface, (padding, padding))

    def _on_event_fired(self, payload: dict) -> None:
        event = payload.get("event")
        scene = None
        if event and getattr(event, "scene", None):
            scene = ScenePayload(
                image=getattr(event.scene, "image", None),
                caption=getattr(event.scene, "caption", None),
            )
        if scene:
            self.show(scene.image, scene.caption)

    def _on_policy_overlay(self, payload: dict) -> None:
        caption = payload.get("caption")
        if caption:
            self.show(payload.get("image"), caption)

    def _on_curriculum_overlay(self, payload: dict) -> None:
        caption = payload.get("caption")
        if caption:
            self.show(payload.get("image"), caption)
