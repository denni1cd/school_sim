"""Event and scene models used by the event system."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


class EventValidationError(ValueError):
    """Raised when an Event payload fails validation."""


def _validate_time_format(value: str) -> None:
    """Raise when the provided time string is not an HH:MM timestamp."""
    if len(value) != 5 or value[2] != ":":
        raise EventValidationError(f"Invalid time format '{value}'. Expected HH:MM.")
    hours, minutes = value.split(":")
    if not hours.isdigit() or not minutes.isdigit():
        raise EventValidationError(f"Invalid time digits in '{value}'.")
    h = int(hours)
    m = int(minutes)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise EventValidationError(f"Time '{value}' out of range.")


@dataclass
class Scene:
    """Information describing the image and caption to render."""

    image: Optional[str] = None
    caption: Optional[str] = None

    def validate(self) -> None:
        """Ensure the scene entry includes the required image data."""
        if self.image is None:
            raise EventValidationError("Scene entries require an 'image' value.")


@dataclass
class Event:
    """Validated event definition along with optional timing/scene metadata."""

    id: str
    when: Optional[str] = None
    room: Optional[str] = None
    condition: Optional[str] = None
    scene: Optional[Scene] = None
    once: bool = False
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the identifier, timing, and scene payload after initialization."""
        if not self.id:
            raise EventValidationError("Event id must be a non-empty string.")
        if self.when:
            _validate_time_format(self.when)
        if self.scene:
            self.scene.validate()
