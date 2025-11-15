"""
Technomancy staging package marker for school_sim.

Extends sys.path so staging modules override production copies during tests.
"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)  # type: ignore[name-defined]
__path__ = sorted(__path__, key=lambda p: (0 if "technomancy" in p else 1, p))  # staging paths first
__all__: list[str] = []
