"""
Unit tests for the V0.7.2 analysis infrastructure.
"""

from __future__ import annotations

import unittest

from analysis.analyzer import AnalysisReport
from analysis.calibration import CalibrationEngine
from analysis.detectors.dimension_detector import DimensionCandidate
from analysis.detectors.unit_detector import UnitDetector
from core.project import Project
from graphics.dxf_item import DXFItem
from model.dxf import DXFDocument, DXFLine


class AnalysisInfrastructureTest(unittest.TestCase):
    """
    Validate analysis classes without Qt.
    """

    def test_unit_detector_reads_known_units(self):
        detector = UnitDetector()

        self.assertEqual(detector.detect({"$INSUNITS": 4}).unit, "mm")
        self.assertEqual(detector.detect({"$INSUNITS": 5}).unit, "cm")
        self.assertEqual(detector.detect({"$INSUNITS": 6}).unit, "m")
        self.assertEqual(detector.detect({"$INSUNITS": 1}).unit, "in")

    def test_unit_detector_reports_unknown_unit(self):
        result = UnitDetector().detect({"$INSUNITS": 0})

        self.assertEqual(result.unit, "unknown")
        self.assertEqual(result.confidence, 0.0)
        self.assertTrue(result.warnings)

    def test_calibration_engine_computes_scale_factor(self):
        dimensions = [
            DimensionCandidate(
                value_text="4.50",
                position=(0.0, 0.0),
                entity_type="DIMENSION",
                measured_length=372.18,
                numeric_value=4.50,
            )
        ]

        result = CalibrationEngine(real_unit="m").calibrate(dimensions)

        self.assertAlmostEqual(result.scale_factor, 0.0120909237)
        self.assertEqual(result.real_unit, "m")
        self.assertGreater(result.confidence, 0.0)

    def test_calibration_engine_warns_on_inconsistent_dimensions(self):
        dimensions = [
            DimensionCandidate(
                value_text="4.00",
                position=(0.0, 0.0),
                entity_type="DIMENSION",
                measured_length=100.0,
                numeric_value=4.0,
            ),
            DimensionCandidate(
                value_text="8.00",
                position=(0.0, 0.0),
                entity_type="DIMENSION",
                measured_length=100.0,
                numeric_value=8.0,
            ),
        ]

        result = CalibrationEngine(
            inconsistency_threshold=0.10
        ).calibrate(dimensions)

        self.assertTrue(result.warnings)
        self.assertLess(result.confidence, 0.8)

    def test_analysis_report_serialization_roundtrip(self):
        report = AnalysisReport(
            detected_unit="m",
            dimension_count=2,
            scale_factor=0.01,
            real_unit="cm",
            confidence=0.75,
            warnings=["warning"],
            errors=["error"],
            pipeline_steps=["unit_detection", "analysis_report"],
        )

        restored = AnalysisReport.from_dict(report.to_dict())

        self.assertEqual(restored.detected_unit, "m")
        self.assertEqual(restored.dimension_count, 2)
        self.assertEqual(restored.scale_factor, 0.01)
        self.assertEqual(restored.real_unit, "cm")
        self.assertEqual(restored.warnings, ["warning"])
        self.assertEqual(restored.errors, ["error"])

    def test_project_stores_latest_analysis_report(self):
        project = Project()
        report = AnalysisReport(detected_unit="cm")

        project.set_analysis_report(report)

        data = project.to_dict()
        self.assertEqual(project.analysis_report, report)
        self.assertEqual(data["analysis_report"]["detected_unit"], "cm")

    def test_dimension_detector_finds_rochette_vectorized_dimension(self):
        from pathlib import Path

        from analysis.detectors.dimension_detector import DimensionDetector

        dxf_path = Path(__file__).resolve().parents[1] / "rochette.dxf"
        result = DimensionDetector().detect(dxf_path)

        values = [
            dimension.value_text
            for dimension in result.dimensions
        ]

        self.assertIn("410", values)

    def test_dxf_item_applies_calibration_scale(self):
        document = DXFDocument(
            entities=[
                DXFLine(
                    x1=0.0,
                    y1=0.0,
                    x2=0.0,
                    y2=10.0,
                )
            ]
        )

        item = DXFItem(
            document,
            scale_factor=2.0,
        )

        self.assertAlmostEqual(item.boundingRect().height(), 20.0)


if __name__ == "__main__":
    unittest.main()
