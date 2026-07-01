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
from analysis.detectors.wall_detector import WallDetectionResult, WallDetector
from importer.dxf_importer import DXFImporter
from model.architecture import Wall


@dataclass(frozen=True)
class AnalysisReport:
    """
    Serializable report produced by BuildingAnalyzer.
    """

    detected_unit: str = "unknown"
    dimension_count: int = 0
    scale_factor: float | None = None
    real_unit: str = "cm"
    wall_count: int = 0
    segments_analyzed: int = 0
    segments_ignored: int = 0
    duplicates_removed: int = 0
    average_wall_confidence: float = 0.0
    detected_walls: list[Wall] = field(default_factory=list)
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
            "wall_count": self.wall_count,
            "segments_analyzed": self.segments_analyzed,
            "segments_ignored": self.segments_ignored,
            "duplicates_removed": self.duplicates_removed,
            "average_wall_confidence": self.average_wall_confidence,
            "detected_walls": [
                wall.to_dict()
                for wall in self.detected_walls
            ],
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
            wall_count=data.get("wall_count", 0),
            segments_analyzed=data.get("segments_analyzed", 0),
            segments_ignored=data.get("segments_ignored", 0),
            duplicates_removed=data.get("duplicates_removed", 0),
            average_wall_confidence=data.get("average_wall_confidence", 0.0),
            detected_walls=[
                Wall.from_dict(wall_data)
                for wall_data in data.get("detected_walls", [])
            ],
            confidence=data.get("confidence", 0.0),
            warnings=list(data.get("warnings", [])),
            errors=list(data.get("errors", [])),
            pipeline_steps=list(data.get("pipeline_steps", [])),
        )


class BuildingAnalyzer:
    """
    Orchestrate the building analysis pipeline.
    """

    PIPELINE_STEPS = [
        "unit_detection",
        "calibration",
        "wall_detection",
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
            wall_result=wall_result,
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
        wall_result: WallDetectionResult,
        warnings: list[str],
        errors: list[str],
    ) -> AnalysisReport:
        return AnalysisReport(
            detected_unit=unit_detection.unit,
            dimension_count=dimension_count,
            scale_factor=calibration.scale_factor,
            real_unit=calibration.real_unit,
            wall_count=len(wall_result.walls),
            segments_analyzed=wall_result.segments_analyzed,
            segments_ignored=wall_result.segments_ignored,
            duplicates_removed=wall_result.duplicates_removed,
            average_wall_confidence=wall_result.average_confidence,
            detected_walls=list(wall_result.walls),
            confidence=self._combined_confidence(
                unit_detection.confidence,
                calibration.confidence,
                wall_result.confidence,
            ),
            warnings=warnings,
            errors=errors,
            pipeline_steps=list(self.PIPELINE_STEPS),
        )

    @staticmethod
    def _combined_confidence(
        unit_confidence: float,
        calibration_confidence: float,
        wall_confidence: float,
    ) -> float:
        scores = [
            score
            for score in (
                unit_confidence,
                calibration_confidence,
                wall_confidence,
            )
            if score > 0
        ]

        if not scores:
            return 0.0

        return sum(scores) / len(scores)
