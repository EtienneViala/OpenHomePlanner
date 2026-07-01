"""
Automatic wall detector for imported DXF documents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import atan2, degrees, hypot
from typing import Any

from model.architecture import DEFAULT_WALL_THICKNESS, Wall
from model.dxf import DXFLine, DXFPolyline


Point = tuple[float, float]


@dataclass(frozen=True)
class WallSegment:
    """
    Normalized project-space segment extracted from DXF geometry.
    """

    start: Point
    end: Point
    source_type: str
    layer: str = "0"

    @property
    def length(self) -> float:
        return hypot(
            self.end[0] - self.start[0],
            self.end[1] - self.start[1],
        )

    @property
    def angle(self) -> float:
        angle = atan2(
            self.end[1] - self.start[1],
            self.end[0] - self.start[0],
        )

        if angle < 0:
            angle += 3.141592653589793

        if angle >= 3.141592653589793:
            angle -= 3.141592653589793

        return angle

    @property
    def direction(self) -> Point:
        length = self.length

        if length <= 0.0:
            return (1.0, 0.0)

        dx = (self.end[0] - self.start[0]) / length
        dy = (self.end[1] - self.start[1]) / length

        if dx < 0 or (abs(dx) <= 0.000001 and dy < 0):
            return (-dx, -dy)

        return (dx, dy)


@dataclass(frozen=True)
class WallDetectionResult:
    """
    Result produced by WallDetector.
    """

    walls: list[Wall] = field(default_factory=list)
    segments_analyzed: int = 0
    segments_ignored: int = 0
    warnings: list[str] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "walls": [
                wall.to_dict()
                for wall in self.walls
            ],
            "segments_analyzed": self.segments_analyzed,
            "segments_ignored": self.segments_ignored,
            "warnings": list(self.warnings),
            "confidence": self.confidence,
        }


class WallDetector:
    """
    Detect first-pass wall centerlines from pairs of close parallel segments.

    The detector intentionally stays conservative: it extracts LINE and
    LWPOLYLINE segments, filters tiny geometry, lightly merges collinear
    fragments, then creates one Wall for each plausible close parallel pair.
    """

    def __init__(
        self,
        min_segment_length: float = 40.0,
        min_wall_thickness: float = 5.0,
        max_wall_thickness: float = 60.0,
        angle_tolerance_degrees: float = 5.0,
        merge_offset_tolerance: float = 3.0,
        merge_gap_tolerance: float = 25.0,
    ):
        self.min_segment_length = min_segment_length
        self.min_wall_thickness = min_wall_thickness
        self.max_wall_thickness = max_wall_thickness
        self.angle_tolerance = angle_tolerance_degrees
        self.merge_offset_tolerance = merge_offset_tolerance
        self.merge_gap_tolerance = merge_gap_tolerance

    def detect(self, source: Any, calibration=None) -> WallDetectionResult:
        document = source if hasattr(source, "entities") else None

        if document is None:
            return WallDetectionResult(
                warnings=["Aucun document DXF disponible pour les murs."]
            )

        scale_factor = self._scale_factor(calibration)
        warnings: list[str] = []

        if scale_factor == 1.0:
            warnings.append(
                "Detection des murs lancee sans echelle calibree fiable."
            )

        raw_segments = self._extract_segments(document, scale_factor)
        usable_segments: list[WallSegment] = []
        ignored = 0

        for segment in raw_segments:
            if segment.length < self.min_segment_length:
                ignored += 1
                continue

            usable_segments.append(segment)

        merged_segments = self._merge_collinear_segments(usable_segments)
        walls = self._walls_from_parallel_pairs(merged_segments)

        if not walls:
            warnings.append("Aucun mur probable detecte dans le DXF.")

        confidence = self._confidence(
            wall_count=len(walls),
            segment_count=len(merged_segments),
            has_scale=scale_factor != 1.0,
        )

        return WallDetectionResult(
            walls=walls,
            segments_analyzed=len(raw_segments),
            segments_ignored=ignored,
            warnings=warnings,
            confidence=confidence,
        )

    def _extract_segments(
        self,
        document,
        scale_factor: float,
    ) -> list[WallSegment]:
        segments: list[WallSegment] = []

        for entity in document.entities:
            if isinstance(entity, DXFLine):
                segments.append(
                    WallSegment(
                        start=(entity.x1 * scale_factor, entity.y1 * scale_factor),
                        end=(entity.x2 * scale_factor, entity.y2 * scale_factor),
                        source_type="LINE",
                        layer=entity.layer,
                    )
                )
                continue

            if isinstance(entity, DXFPolyline):
                segments.extend(
                    self._segments_from_polyline(entity, scale_factor)
                )

        return segments

    def _segments_from_polyline(
        self,
        entity: DXFPolyline,
        scale_factor: float,
    ) -> list[WallSegment]:
        pairs = list(zip(entity.points, entity.points[1:]))

        if entity.closed and len(entity.points) > 1:
            pairs.append((entity.points[-1], entity.points[0]))

        return [
            WallSegment(
                start=(
                    float(start[0]) * scale_factor,
                    float(start[1]) * scale_factor,
                ),
                end=(
                    float(end[0]) * scale_factor,
                    float(end[1]) * scale_factor,
                ),
                source_type="LWPOLYLINE",
                layer=entity.layer,
            )
            for start, end in pairs
        ]

    def _merge_collinear_segments(
        self,
        segments: list[WallSegment],
    ) -> list[WallSegment]:
        remaining = list(segments)
        merged: list[WallSegment] = []

        while remaining:
            base = remaining.pop(0)
            direction = base.direction
            normal = (-direction[1], direction[0])
            base_offset = self._dot(base.start, normal)
            spans = [self._span(base, direction)]
            layers = {base.layer}
            changed = True

            while changed:
                changed = False

                for candidate in list(remaining):
                    if self._angle_difference(base, candidate) > self.angle_tolerance:
                        continue

                    offset = self._dot(candidate.start, normal)

                    if abs(offset - base_offset) > self.merge_offset_tolerance:
                        continue

                    candidate_span = self._span(candidate, direction)

                    if not self._touches_any_span(candidate_span, spans):
                        continue

                    spans.append(candidate_span)
                    layers.add(candidate.layer)
                    remaining.remove(candidate)
                    changed = True

            start_t = min(span[0] for span in spans)
            end_t = max(span[1] for span in spans)
            origin = self._scale(direction, start_t)
            end = self._scale(direction, end_t)
            offset_vector = self._scale(normal, base_offset)

            merged.append(
                WallSegment(
                    start=self._add(origin, offset_vector),
                    end=self._add(end, offset_vector),
                    source_type="MERGED",
                    layer=",".join(sorted(layers)),
                )
            )

        return merged

    def _walls_from_parallel_pairs(
        self,
        segments: list[WallSegment],
    ) -> list[Wall]:
        walls: list[Wall] = []
        used_pairs: set[tuple[int, int]] = set()

        for index, first in enumerate(segments):
            for second_index in range(index + 1, len(segments)):
                second = segments[second_index]

                if self._angle_difference(first, second) > self.angle_tolerance:
                    continue

                wall_data = self._wall_from_pair(first, second)

                if wall_data is None:
                    continue

                signature = self._wall_signature(wall_data)

                if signature in used_pairs:
                    continue

                used_pairs.add(signature)
                walls.append(wall_data)

        return walls

    def _wall_from_pair(
        self,
        first: WallSegment,
        second: WallSegment,
    ) -> Wall | None:
        direction = first.direction
        normal = (-direction[1], direction[0])
        distance = abs(
            self._dot(second.start, normal) - self._dot(first.start, normal)
        )

        if (
            distance < self.min_wall_thickness
            or distance > self.max_wall_thickness
        ):
            return None

        first_span = self._span(first, direction)
        second_span = self._span(second, direction)
        overlap_start = max(first_span[0], second_span[0])
        overlap_end = min(first_span[1], second_span[1])

        if overlap_end - overlap_start < self.min_segment_length:
            return None

        first_offset = self._dot(first.start, normal)
        second_offset = self._dot(second.start, normal)
        center_offset = (first_offset + second_offset) / 2.0
        start = self._add(
            self._scale(direction, overlap_start),
            self._scale(normal, center_offset),
        )
        end = self._add(
            self._scale(direction, overlap_end),
            self._scale(normal, center_offset),
        )

        return Wall(
            name="Mur detecte",
            start=start,
            end=end,
            thickness=distance or DEFAULT_WALL_THICKNESS,
            orientation=degrees(atan2(direction[1], direction[0])),
        )

    def _wall_signature(self, wall: Wall) -> tuple[int, int]:
        points = sorted([wall.start, wall.end])
        return (
            hash((
                round(points[0][0], 1),
                round(points[0][1], 1),
                round(points[1][0], 1),
                round(points[1][1], 1),
            )),
            round(wall.thickness),
        )

    def _touches_any_span(
        self,
        candidate: tuple[float, float],
        spans: list[tuple[float, float]],
    ) -> bool:
        return any(
            candidate[0] <= span[1] + self.merge_gap_tolerance
            and candidate[1] >= span[0] - self.merge_gap_tolerance
            for span in spans
        )

    def _angle_difference(
        self,
        first: WallSegment,
        second: WallSegment,
    ) -> float:
        diff = abs(degrees(first.angle - second.angle)) % 180.0
        return min(diff, 180.0 - diff)

    @staticmethod
    def _scale_factor(calibration) -> float:
        value = getattr(calibration, "scale_factor", None)

        if value is None or value <= 0:
            return 1.0

        return float(value)

    @staticmethod
    def _confidence(
        wall_count: int,
        segment_count: int,
        has_scale: bool,
    ) -> float:
        if wall_count <= 0 or segment_count <= 0:
            return 0.0

        ratio = min(1.0, wall_count / max(1.0, segment_count / 4.0))
        confidence = 0.35 + (ratio * 0.4)

        if has_scale:
            confidence += 0.15

        return min(0.9, confidence)

    @staticmethod
    def _span(segment: WallSegment, direction: Point) -> tuple[float, float]:
        values = (
            WallDetector._dot(segment.start, direction),
            WallDetector._dot(segment.end, direction),
        )
        return (min(values), max(values))

    @staticmethod
    def _dot(first: Point, second: Point) -> float:
        return first[0] * second[0] + first[1] * second[1]

    @staticmethod
    def _add(first: Point, second: Point) -> Point:
        return (first[0] + second[0], first[1] + second[1])

    @staticmethod
    def _scale(point: Point, factor: float) -> Point:
        return (point[0] * factor, point[1] * factor)
