"""
Opening detector skeleton.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OpeningDetectionResult:
    """
    Placeholder opening detection result.
    """

    openings: list = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "openings": list(self.openings),
            "warnings": list(self.warnings),
        }


class OpeningDetector:
    """
    Future automatic door and window detector.

    V0.7.2 intentionally does not recognize openings. This detector only
    reserves the pipeline slot and returns an empty result.
    """

    def detect(self, source: Any, walls=None) -> OpeningDetectionResult:
        return OpeningDetectionResult(
            warnings=["Detection automatique des ouvertures non implementee."]
        )

