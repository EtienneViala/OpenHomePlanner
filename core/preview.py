"""
Pure data definitions for placement previews.
"""

from __future__ import annotations

from dataclasses import dataclass


ColorTuple = tuple[int, int, int]


@dataclass(frozen=True)
class PreviewDefinition:
    """
    Description of a temporary placement preview.

    This class intentionally contains no Qt type. Tools may return it to
    describe the preview they need, while the graphics layer decides how to
    render it.
    """

    shape: str
    size: float = 24.0
    line_color: ColorTuple = (0, 220, 255)
    fill_color: ColorTuple = (30, 30, 30)
    opacity: float = 0.5
    z_value: float = 10_000.0
