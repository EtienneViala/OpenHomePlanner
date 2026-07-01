"""
Building analysis pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from analysis.calibration import CalibrationEngine, CalibrationResult
from analysis.detectors.dimension_detector import DimensionDetector
from analysis.detectors.opening_detector import OpeningDetector
from analysis.detectors.room_detector import RoomDetector
from analysis.detectors.unit_detector import UnitDetection, UnitDetector
from analysis.detectors.wall_detector import WallDetector
from importer.dxf_importer import DXFImporter


@dataclass(frozen=True)
class AnalysisReport:
    """
    Serializable report produced by BuildingAnalyzer.
    """

    detected_unit: str = "unknown"
    dimension_count: int = 0
    scale_factor: float | None = None
    real_unit: str = "cm"
    confidence: float = 0.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    pipeline_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "detected_unit": self.detected_unit,
            "dimension_count": self.dimension_count,
            "scale_factor": self.scale_factor,
            "real_unit": self.real_unit,
            "confidence": self.confidence,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "pipeline_steps": list(self.pipeline_steps),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalysisReport":
        return cls(
            detected_unit=data.get("detected_unit", "unknown"),
            dimension_count=data.get("dimension_count", 0),
            scale_factor=data.get("scale_factor"),
            real_unit=data.get("real_unit", "cm"),
            confidence=data.get("confidence", 0.0),
            warnings=list(data.get("warnings", [])),
            errors=list(data.get("errors", [])),
            pipeline_steps=list(data.get("pipeline_steps", [])),
        )


class BuildingAnalyzer:
    """
    Orchestrate the V0.7.2 building analysis pipeline.
    """

    PIPELINE_STEPS = [
        "unit_detection",
        "calibration",
        "wall_detection_placeholder",
        "opening_detection_placeholder",
        "room_detection_placeholder",
        "analysis_report",
    ]

    def __init__(
        self,
        unit_detector: UnitDetector | None = None,
        dimension_detector: DimensionDetector | None = None,
        calibration_engine: CalibrationEngine | None = None,
        wall_detector: WallDetector | None = None,
        opening_detector: OpeningDetector | None = None,
        room_detector: RoomDetector | None = None,
    ):
        self.unit_detector = unit_detector or UnitDetector()
        self.dimension_detector = dimension_detector or DimensionDetector()
        self.calibration_engine = calibration_engine or CalibrationEngine()
        self.wall_detector = wall_detector or WallDetector()
        self.opening_detector = opening_detector or OpeningDetector()
        self.room_detector = room_detector or RoomDetector()

    def analyze(self, source: Any) -> AnalysisReport:
        """
        Analyze a DXF path or document and return a serializable report.
        """
        dxf_source = self._load_document_if_needed(source)
        warnings: list[str] = []
        errors: list[str] = []

        unit_detection = self.unit_detector.detect(source)
        warnings.extend(unit_detection.warnings)

        dimension_result = self.dimension_detector.detect(source)
        warnings.extend(dimension_result.warnings)

        calibration = self.calibration_engine.calibrate(
            dimension_result.dimensions
        )
        warnings.extend(calibration.warnings)
        errors.extend(calibration.errors)

        wall_result = self.wall_detector.detect(dxf_source, calibration)
        warnings.extend(wall_result.warnings)

        opening_result = self.opening_detector.detect(
            dxf_source,
            wall_result.walls,
        )
        warnings.extend(opening_result.warnings)

        room_result = self.room_detector.detect(
            dxf_source,
            wall_result.walls,
            opening_result.openings,
        )
        warnings.extend(room_result.warnings)

        return self._build_report(
            unit_detection=unit_detection,
            dimension_count=len(dimension_result.dimensions),
            calibration=calibration,
            warnings=warnings,
            errors=errors,
        )

    def _load_document_if_needed(self, source: Any):
        if not isinstance(source, (str, Path)):
            return source

        return DXFImporter().load(str(source))

    def _build_report(
        self,
        unit_detection: UnitDetection,
        dimension_count: int,
        calibration: CalibrationResult,
        warnings: list[str],
        errors: list[str],
    ) -> AnalysisReport:
        return AnalysisReport(
            detected_unit=unit_detection.unit,
            dimension_count=dimension_count,
            scale_factor=calibration.scale_factor,
            real_unit=calibration.real_unit,
            confidence=self._combined_confidence(
                unit_detection.confidence,
                calibration.confidence,
            ),
            warnings=warnings,
            errors=errors,
            pipeline_steps=list(self.PIPELINE_STEPS),
        )

    @staticmethod
    def _combined_confidence(unit_confidence: float, calibration_confidence: float) -> float:
        if calibration_confidence <= 0:
            return unit_confidence

        return (unit_confidence + calibration_confidence) / 2.0
