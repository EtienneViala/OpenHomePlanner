"""
Wall detector skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class WallDetectionResult:
    """
    Placeholder wall detection result.
    """

    walls: list = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "walls": list(self.walls),
            "warnings": list(self.warnings),
        }


class WallDetector:
    """
    Future automatic wall detector.

    V0.7.2 intentionally does not recognize walls. This detector only reserves
    the pipeline slot and returns an empty result.
    """

    def detect(self, source: Any, calibration=None) -> WallDetectionResult:
        return WallDetectionResult(
            warnings=["Detection automatique des murs non implementee."]
        )

