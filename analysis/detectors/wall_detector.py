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
class WallDetectionSettings:
    """
    Centralized tolerances for first-pass wall detection.
    """

    min_segment_length: float = 40.0
    min_wall_length: float = 60.0
    min_wall_thickness: float = 5.0
    max_wall_thickness: float = 60.0
    preferred_min_thickness: float = 8.0
    preferred_max_thickness: float = 35.0
    angle_tolerance_degrees: float = 5.0
    merge_offset_tolerance: float = 3.0
    merge_gap_tolerance: float = 25.0
    min_wall_confidence: float = 0.45
    duplicate_length_tolerance: float = 15.0
    duplicate_length_ratio: float = 0.08
    duplicate_angle_tolerance: float = 3.0
    duplicate_center_tolerance: float = 12.0
    duplicate_endpoint_tolerance: float = 18.0
    annotation_layer_keywords: tuple[str, ...] = (
        "anno",
        "annotation",
        "cote",
        "cot",
        "dim",
        "dimension",
        "text",
        "texte",
    )


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
    duplicates_removed: int = 0
    average_confidence: float = 0.0
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
            "duplicates_removed": self.duplicates_removed,
            "average_confidence": self.average_confidence,
            "warnings": list(self.warnings),
            "confidence": self.confidence,
        }


class WallDetector:
    """
    Detect first-pass wall centerlines from pairs of close parallel segments.
    """

    def __init__(
        self,
        settings: WallDetectionSettings | None = None,
        min_segment_length: float | None = None,
        min_wall_thickness: float | None = None,
        max_wall_thickness: float | None = None,
        angle_tolerance_degrees: float | None = None,
        merge_offset_tolerance: float | None = None,
        merge_gap_tolerance: float | None = None,
    ):
        self.settings = settings or WallDetectionSettings()

        if min_segment_length is not None:
            self.settings = self._replace_setting(
                "min_segment_length",
                min_segment_length,
            )
        if min_wall_thickness is not None:
            self.settings = self._replace_setting(
                "min_wall_thickness",
                min_wall_thickness,
            )
        if max_wall_thickness is not None:
            self.settings = self._replace_setting(
                "max_wall_thickness",
                max_wall_thickness,
            )
        if angle_tolerance_degrees is not None:
            self.settings = self._replace_setting(
                "angle_tolerance_degrees",
                angle_tolerance_degrees,
            )
        if merge_offset_tolerance is not None:
            self.settings = self._replace_setting(
                "merge_offset_tolerance",
                merge_offset_tolerance,
            )
        if merge_gap_tolerance is not None:
            self.settings = self._replace_setting(
                "merge_gap_tolerance",
                merge_gap_tolerance,
            )

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
            if self._ignore_segment(segment):
                ignored += 1
                continue

            usable_segments.append(segment)

        merged_segments = self._merge_collinear_segments(usable_segments)
        candidates = self._walls_from_parallel_pairs(
            merged_segments,
            has_scale=scale_factor != 1.0,
        )
        walls, duplicates_removed = self._remove_duplicate_walls(candidates)

        if not walls:
            warnings.append("Aucun mur probable detecte dans le DXF.")

        average_confidence = self._average_wall_confidence(walls)

        return WallDetectionResult(
            walls=walls,
            segments_analyzed=len(raw_segments),
            segments_ignored=ignored,
            duplicates_removed=duplicates_removed,
            average_confidence=average_confidence,
            warnings=warnings,
            confidence=self._global_confidence(
                wall_count=len(walls),
                segment_count=len(merged_segments),
                average_confidence=average_confidence,
                has_scale=scale_factor != 1.0,
            ),
        )

    def _extract_segments(
        self,
        document,
        scale_factor: float,
    ) -> list[WallSegment]:
        segments: list[WallSegment] = []

        for entity in document.entities:
            if self._is_annotation_layer(getattr(entity, "layer", "")):
                continue

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

    def _ignore_segment(self, segment: WallSegment) -> bool:
        return (
            segment.length < self.settings.min_segment_length
            or self._is_annotation_layer(segment.layer)
        )

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
                    if (
                        self._angle_difference(base, candidate)
                        > self.settings.angle_tolerance_degrees
                    ):
                        continue

                    offset = self._dot(candidate.start, normal)

                    if (
                        abs(offset - base_offset)
                        > self.settings.merge_offset_tolerance
                    ):
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
        has_scale: bool,
    ) -> list[Wall]:
        walls: list[Wall] = []

        for index, first in enumerate(segments):
            for second_index in range(index + 1, len(segments)):
                second = segments[second_index]

                if (
                    self._angle_difference(first, second)
                    > self.settings.angle_tolerance_degrees
                ):
                    continue

                wall = self._wall_from_pair(
                    first,
                    second,
                    has_scale=has_scale,
                )

                if wall is None:
                    continue

                walls.append(wall)

        return walls

    def _wall_from_pair(
        self,
        first: WallSegment,
        second: WallSegment,
        has_scale: bool,
    ) -> Wall | None:
        direction = first.direction
        normal = (-direction[1], direction[0])
        distance = abs(
            self._dot(second.start, normal) - self._dot(first.start, normal)
        )

        if (
            distance < self.settings.min_wall_thickness
            or distance > self.settings.max_wall_thickness
        ):
            return None

        first_span = self._span(first, direction)
        second_span = self._span(second, direction)
        overlap_start = max(first_span[0], second_span[0])
        overlap_end = min(first_span[1], second_span[1])
        wall_length = overlap_end - overlap_start

        if wall_length < self.settings.min_wall_length:
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
        confidence = self._wall_confidence(
            length=wall_length,
            thickness=distance,
            has_scale=has_scale,
        )

        if confidence < self.settings.min_wall_confidence:
            return None

        return Wall(
            name="Mur detecte",
            start=start,
            end=end,
            thickness=distance or DEFAULT_WALL_THICKNESS,
            orientation=degrees(atan2(direction[1], direction[0])),
            source="detected",
            confidence=confidence,
            detection_id=self._detection_id(start, end, distance),
            metadata={
                "detector": "WallDetector",
                "source_segments": [first.source_type, second.source_type],
                "layers": sorted({first.layer, second.layer}),
            },
        )

    def _remove_duplicate_walls(
        self,
        walls: list[Wall],
    ) -> tuple[list[Wall], int]:
        sorted_walls = sorted(
            walls,
            key=lambda wall: (
                -getattr(wall, "confidence", 0.0),
                -wall.length,
            ),
        )
        unique: list[Wall] = []
        duplicates = 0

        for wall in sorted_walls:
            if any(self._is_duplicate_wall(wall, kept) for kept in unique):
                duplicates += 1
                continue

            unique.append(wall)

        unique.sort(
            key=lambda wall: (
                round(self._center(wall)[1], 3),
                round(self._center(wall)[0], 3),
            )
        )

        return unique, duplicates

    def _is_duplicate_wall(self, first: Wall, second: Wall) -> bool:
        length_tolerance = max(
            self.settings.duplicate_length_tolerance,
            max(first.length, second.length)
            * self.settings.duplicate_length_ratio,
        )

        if abs(first.length - second.length) > length_tolerance:
            return False

        if (
            self._wall_angle_difference(first, second)
            > self.settings.duplicate_angle_tolerance
        ):
            return False

        if (
            self._distance(self._center(first), self._center(second))
            > self.settings.duplicate_center_tolerance
        ):
            return False

        direct = (
            self._distance(first.start, second.start)
            + self._distance(first.end, second.end)
        ) / 2.0
        reversed_order = (
            self._distance(first.start, second.end)
            + self._distance(first.end, second.start)
        ) / 2.0

        return (
            min(direct, reversed_order)
            <= self.settings.duplicate_endpoint_tolerance
        )

    def has_obvious_duplicates(self, walls: list[Wall]) -> bool:
        """
        Return True when a list of walls still contains an obvious duplicate.
        """
        for index, first in enumerate(walls):
            for second in walls[index + 1:]:
                if self._is_duplicate_wall(first, second):
                    return True

        return False

    def _wall_confidence(
        self,
        length: float,
        thickness: float,
        has_scale: bool,
    ) -> float:
        confidence = 0.35

        if length >= self.settings.min_wall_length * 2.0:
            confidence += 0.20
        elif length >= self.settings.min_wall_length:
            confidence += 0.10

        if (
            self.settings.preferred_min_thickness
            <= thickness
            <= self.settings.preferred_max_thickness
        ):
            confidence += 0.25
        else:
            confidence += 0.10

        if has_scale:
            confidence += 0.10

        return min(0.95, confidence)

    def _touches_any_span(
        self,
        candidate: tuple[float, float],
        spans: list[tuple[float, float]],
    ) -> bool:
        return any(
            candidate[0] <= span[1] + self.settings.merge_gap_tolerance
            and candidate[1] >= span[0] - self.settings.merge_gap_tolerance
            for span in spans
        )

    def _angle_difference(
        self,
        first: WallSegment,
        second: WallSegment,
    ) -> float:
        diff = abs(degrees(first.angle - second.angle)) % 180.0
        return min(diff, 180.0 - diff)

    def _is_annotation_layer(self, layer: str) -> bool:
        normalized = str(layer).lower()

        return any(
            keyword in normalized
            for keyword in self.settings.annotation_layer_keywords
        )

    @staticmethod
    def _scale_factor(calibration) -> float:
        value = getattr(calibration, "scale_factor", None)

        if value is None or value <= 0:
            return 1.0

        return float(value)

    @staticmethod
    def _global_confidence(
        wall_count: int,
        segment_count: int,
        average_confidence: float,
        has_scale: bool,
    ) -> float:
        if wall_count <= 0 or segment_count <= 0:
            return 0.0

        ratio = min(1.0, wall_count / max(1.0, segment_count / 4.0))
        confidence = (average_confidence * 0.75) + (ratio * 0.15)

        if has_scale:
            confidence += 0.10

        return min(0.95, confidence)

    @staticmethod
    def _average_wall_confidence(walls: list[Wall]) -> float:
        if not walls:
            return 0.0

        return sum(getattr(wall, "confidence", 0.0) for wall in walls) / len(walls)

    @staticmethod
    def _span(segment: WallSegment, direction: Point) -> tuple[float, float]:
        values = (
            WallDetector._dot(segment.start, direction),
            WallDetector._dot(segment.end, direction),
        )
        return (min(values), max(values))

    @staticmethod
    def _wall_angle_difference(first: Wall, second: Wall) -> float:
        diff = abs(first.angle - second.angle) % 180.0
        return min(diff, 180.0 - diff)

    @staticmethod
    def _center(wall: Wall) -> Point:
        return (
            (wall.start[0] + wall.end[0]) / 2.0,
            (wall.start[1] + wall.end[1]) / 2.0,
        )

    @staticmethod
    def _distance(first: Point, second: Point) -> float:
        return hypot(first[0] - second[0], first[1] - second[1])

    @staticmethod
    def _detection_id(start: Point, end: Point, thickness: float) -> str:
        points = sorted([start, end])
        return (
            "wall:"
            f"{points[0][0]:.1f}:"
            f"{points[0][1]:.1f}:"
            f"{points[1][0]:.1f}:"
            f"{points[1][1]:.1f}:"
            f"{thickness:.1f}"
        )

    @staticmethod
    def _dot(first: Point, second: Point) -> float:
        return first[0] * second[0] + first[1] * second[1]

    @staticmethod
    def _add(first: Point, second: Point) -> Point:
        return (first[0] + second[0], first[1] + second[1])

    @staticmethod
    def _scale(point: Point, factor: float) -> Point:
        return (point[0] * factor, point[1] * factor)

    def _replace_setting(self, name: str, value: float) -> WallDetectionSettings:
        data = self.settings.__dict__.copy()
        data[name] = value
        return WallDetectionSettings(**data)
