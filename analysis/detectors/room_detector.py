"""
Room detector skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RoomDetectionResult:
    """
    Placeholder room detection result.
    """

    rooms: list = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "rooms": list(self.rooms),
            "warnings": list(self.warnings),
        }


class RoomDetector:
    """
    Future automatic room detector.

    V0.7.2 intentionally does not recognize rooms. This detector only reserves
    the pipeline slot and returns an empty result.
    """

    def detect(self, source: Any, walls=None, openings=None) -> RoomDetectionResult:
        return RoomDetectionResult(
            warnings=["Detection automatique des pieces non implementee."]
        )

