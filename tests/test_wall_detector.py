"""
Unit tests for the V0.7.3 wall detector.
"""

from __future__ import annotations

import unittest

from analysis.analyzer import BuildingAnalyzer
from analysis.calibration import CalibrationResult
from analysis.detectors.wall_detector import WallDetector
from core.project import Project
from model.architecture import Wall
from model.dxf import DXFDocument, DXFLine, DXFPolyline


class WallDetectorTest(unittest.TestCase):
    """
    Validate the DXF wall detector without Qt.
    """

    def test_extracts_segments_from_polyline(self):
        document = DXFDocument(
            entities=[
                DXFPolyline(
                    points=[(0.0, 0.0), (100.0, 0.0), (100.0, 50.0)],
                )
            ]
        )

        segments = WallDetector()._extract_segments(document, 1.0)

        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].start, (0.0, 0.0))
        self.assertEqual(segments[0].end, (100.0, 0.0))

    def test_rejects_too_short_segments(self):
        document = DXFDocument(
            entities=[
                DXFLine(x1=0.0, y1=0.0, x2=5.0, y2=0.0),
            ]
        )

        result = WallDetector(
            min_segment_length=40.0,
            merge_offset_tolerance=0.1,
        ).detect(
            document,
            CalibrationResult(scale_factor=1.0),
        )

        self.assertEqual(result.segments_analyzed, 1)
        self.assertEqual(result.segments_ignored, 1)
        self.assertEqual(result.walls, [])

    def test_creates_wall_from_parallel_lines(self):
        document = DXFDocument(
            entities=[
                DXFLine(x1=0.0, y1=0.0, x2=120.0, y2=0.0),
                DXFLine(x1=0.0, y1=20.0, x2=120.0, y2=20.0),
            ]
        )

        result = WallDetector(
            min_segment_length=40.0,
            merge_offset_tolerance=0.1,
        ).detect(
            document,
            CalibrationResult(scale_factor=1.0),
        )

        self.assertEqual(len(result.walls), 1)
        self.assertIsInstance(result.walls[0], Wall)
        self.assertEqual(result.walls[0].start, (0.0, 10.0))
        self.assertEqual(result.walls[0].end, (120.0, 10.0))
        self.assertAlmostEqual(result.walls[0].thickness, 20.0)
        self.assertEqual(result.walls[0].source, "detected")
        self.assertGreater(result.walls[0].confidence, 0.0)
        self.assertTrue(result.walls[0].detection_id)

    def test_applies_calibration_scale_factor(self):
        document = DXFDocument(
            entities=[
                DXFLine(x1=0.0, y1=0.0, x2=100.0, y2=0.0),
                DXFLine(x1=0.0, y1=10.0, x2=100.0, y2=10.0),
            ]
        )

        result = WallDetector(min_segment_length=40.0).detect(
            document,
            CalibrationResult(scale_factor=2.0),
        )

        wall = result.walls[0]
        self.assertEqual(wall.start, (0.0, 10.0))
        self.assertEqual(wall.end, (200.0, 10.0))
        self.assertAlmostEqual(wall.thickness, 20.0)

    def test_building_analyzer_reports_wall_detection(self):
        document = DXFDocument(
            entities=[
                DXFLine(x1=0.0, y1=0.0, x2=120.0, y2=0.0),
                DXFLine(x1=0.0, y1=20.0, x2=120.0, y2=20.0),
            ]
        )
        analyzer = BuildingAnalyzer(
            wall_detector=WallDetector(min_segment_length=40.0),
        )

        report = analyzer.analyze(document)

        self.assertEqual(report.wall_count, 1)
        self.assertEqual(report.segments_analyzed, 2)
        self.assertEqual(len(report.detected_walls), 1)
        self.assertIn("wall_detection", report.pipeline_steps)
        self.assertEqual(report.duplicates_removed, 0)
        self.assertGreater(report.average_wall_confidence, 0.0)

    def test_removes_duplicate_detected_walls(self):
        document = DXFDocument(
            entities=[
                DXFLine(x1=0.0, y1=0.0, x2=120.0, y2=0.0),
                DXFLine(x1=0.0, y1=20.0, x2=120.0, y2=20.0),
                DXFLine(x1=2.0, y1=1.0, x2=122.0, y2=1.0),
                DXFLine(x1=2.0, y1=21.0, x2=122.0, y2=21.0),
            ]
        )

        result = WallDetector(
            min_segment_length=40.0,
            merge_offset_tolerance=0.1,
        ).detect(
            document,
            CalibrationResult(scale_factor=1.0),
        )

        self.assertEqual(len(result.walls), 1)
        self.assertGreaterEqual(result.duplicates_removed, 1)
        self.assertFalse(WallDetector().has_obvious_duplicates(result.walls))

    def test_project_removes_only_detected_walls(self):
        project = Project()
        manual = Wall(
            name="Mur manuel",
            start=(0.0, 0.0),
            end=(100.0, 0.0),
        )
        detected = Wall(
            name="Mur detecte",
            start=(0.0, 20.0),
            end=(100.0, 20.0),
            source="detected",
            confidence=0.75,
        )

        project.add_object(manual)
        project.add_object(detected)
        removed = project.remove_detected_walls()

        self.assertEqual(removed, 1)
        self.assertIn(manual, list(project.objects))
        self.assertNotIn(detected, list(project.objects))
        self.assertEqual(project.house.floors[0].walls, [manual])

    def test_redetection_does_not_accumulate_detected_walls(self):
        document = DXFDocument(
            entities=[
                DXFLine(x1=0.0, y1=0.0, x2=120.0, y2=0.0),
                DXFLine(x1=0.0, y1=20.0, x2=120.0, y2=20.0),
            ]
        )
        analyzer = BuildingAnalyzer(
            wall_detector=WallDetector(min_segment_length=40.0),
        )
        project = Project()
        manual = Wall(start=(0.0, 100.0), end=(120.0, 100.0))
        project.add_object(manual)

        for wall in analyzer.analyze(document).detected_walls:
            project.add_object(wall)

        count_after_first_detection = len(project.objects)
        project.remove_detected_walls()

        for wall in analyzer.analyze(document).detected_walls:
            project.add_object(wall)

        self.assertEqual(len(project.objects), count_after_first_detection)
        self.assertIn(manual, list(project.objects))
        self.assertEqual(len(project.detected_walls()), 1)


if __name__ == "__main__":
    unittest.main()
