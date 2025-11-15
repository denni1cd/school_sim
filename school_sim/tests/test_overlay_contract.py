"""Confirm overlay payloads and policy canvases have the right contract."""

import pygame

from school_sim.events.scene_overlay import SceneOverlay


def test_overlay_show_hide_contract(tmp_path):
    pygame.init()
    overlay = SceneOverlay(base_dir=str(tmp_path))
    overlay.attach(pygame.Surface((64, 64)))

    overlay.show(None, "  Test Caption  ")
    try:
        assert overlay.is_active
        assert overlay.caption == "Test Caption"

        overlay.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        assert not overlay.is_active
        assert overlay.caption is None

        overlay.show("missing.png", "Another")
        assert overlay.is_active
        assert overlay.caption.startswith("(missing image)") or overlay.caption == "Another"
    finally:
        pygame.quit()
