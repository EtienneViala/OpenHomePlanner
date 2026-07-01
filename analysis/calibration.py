"""
Plan calibration engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Iterable


@dataclass(frozen=True)
class CalibrationResult:
    """
    Scale calculation result.
    """

    scale_factor: float | None = None
    real_unit: str = "m"
    confidence: float = 0.0
    sample_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scale_factor": self.scale_factor,
            "real_unit": self.real_unit,
            "confidence": self.confidence,
            "sample_count": self.sample_count,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


class CalibrationEngine:
    """
    Compute drawing scale from detected dimensions.
    """

    def __init__(
        self,
        real_unit: str = "cm",
        inconsistency_threshold: float = 0.15,
    ):
        self.real_unit = real_unit
        self.inconsistency_threshold = inconsistency_threshold

    def calibrate(self, dimensions: Iterable) -> CalibrationResult:
        """
        Average every usable dimension ratio.
        """
        factors: list[float] = []

        for dimension in dimensions:
            numeric_value = getattr(dimension, "numeric_value", None)
            measured_length = getattr(dimension, "measured_length", None)

            if numeric_value is None or measured_length in (None, 0):
                continue

            if numeric_value <= 0 or measured_length <= 0:
                continue

            factors.append(float(numeric_value) / float(measured_length))

        if not factors:
            return CalibrationResult(
                real_unit=self.real_unit,
                warnings=[
                    "Aucune cotation exploitable pour calculer l'echelle."
                ],
            )

        scale_factor = mean(factors)
        warnings: list[str] = []
        confidence = 0.85

        if len(factors) > 1 and scale_factor > 0:
            deviations = [
                abs(factor - scale_factor) / scale_factor
                for factor in factors
            ]
            max_deviation = max(deviations)

            if max_deviation > self.inconsistency_threshold:
                warnings.append(
                    "Ecart important entre plusieurs cotations detectees."
                )
                confidence = 0.45

        return CalibrationResult(
            scale_factor=scale_factor,
            real_unit=self.real_unit,
            confidence=confidence,
            sample_count=len(factors),
            warnings=warnings,
        )
