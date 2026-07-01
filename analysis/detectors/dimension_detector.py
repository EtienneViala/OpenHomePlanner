"""
DXF dimension detector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from pathlib import Path
import re
from typing import Any

import ezdxf

from importer.dxf_importer import DXFImporter
from model.dxf import DXFPolyline


Position = tuple[float, float]


@dataclass(frozen=True)
class DimensionCandidate:
    """
    Textual or native DXF dimension found in a drawing.
    """

    value_text: str
    position: Position
    entity_type: str
    associated_entity: str | None = None
    measured_length: float | None = None
    numeric_value: float | None = None

    def to_dict(self) -> dict:
        return {
            "value_text": self.value_text,
            "position": list(self.position),
            "entity_type": self.entity_type,
            "associated_entity": self.associated_entity,
            "measured_length": self.measured_length,
            "numeric_value": self.numeric_value,
        }


@dataclass(frozen=True)
class DimensionDetectionResult:
    """
    Result produced by DimensionDetector.
    """

    dimensions: list[DimensionCandidate] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "dimensions": [
                dimension.to_dict()
                for dimension in self.dimensions
            ],
            "warnings": list(self.warnings),
        }


class DimensionDetector:
    """
    Find visible dimension hints in TEXT, MTEXT and DIMENSION entities.
    """

    _NUMBER_RE = re.compile(r"[-+]?\d+(?:[.,]\d+)?")

    def detect(self, source: Any) -> DimensionDetectionResult:
        """
        Read a DXF source and return dimension candidates.
        """
        drawing = self._drawing_from_source(source)

        if drawing is None:
            return DimensionDetectionResult(
                warnings=["Aucun dessin DXF disponible pour les cotations."]
            )

        dimensions: list[DimensionCandidate] = []
        warnings: list[str] = []

        for entity in drawing.modelspace():
            entity_type = entity.dxftype()

            if entity_type == "TEXT":
                dimensions.append(self._from_text(entity))
                continue

            if entity_type == "MTEXT":
                dimensions.append(self._from_mtext(entity))
                continue

            if entity_type == "DIMENSION":
                dimensions.append(self._from_dimension(entity))
                continue

        dimensions.extend(
            self._detect_vectorized_dimensions(source)
        )

        return DimensionDetectionResult(
            dimensions=[
                dimension
                for dimension in dimensions
                if dimension.value_text
            ],
            warnings=warnings,
        )

    def _detect_vectorized_dimensions(self, source: Any) -> list[DimensionCandidate]:
        """
        Detect dimensions exported as polylines instead of text entities.

        Some CAD exports explode text and dimensions into LWPOLYLINE geometry.
        This fallback recognizes simple outside dimension lines with nearby
        vectorized numeric glyphs. It prepares calibration without changing the
        DXF display model.
        """
        document = self._document_from_source(source)

        if document is None:
            return []

        candidates: list[DimensionCandidate] = []
        dimension_lines = self._dimension_line_segments(document.entities)
        glyphs = self._small_polyline_glyphs(document.entities)

        for line in dimension_lines:
            value_text = self._read_glyphs_near_line(line, glyphs)

            if value_text is None:
                continue

            candidates.append(
                DimensionCandidate(
                    value_text=value_text,
                    position=(
                        (line["x1"] + line["x2"]) / 2.0,
                        (line["y1"] + line["y2"]) / 2.0,
                    ),
                    entity_type="VECTORIZED_DIMENSION",
                    associated_entity="LWPOLYLINE",
                    measured_length=line["length"],
                    numeric_value=self._numeric_value(value_text),
                )
            )

        return candidates

    def _document_from_source(self, source: Any):
        if hasattr(source, "entities"):
            return source

        filename = self._filename_from_source(source)

        if filename is None:
            return None

        try:
            return DXFImporter().load(str(filename))
        except Exception:  # noqa: BLE001 - fallback detector stays optional
            return None

    def _dimension_line_segments(self, entities: list) -> list[dict]:
        segments: list[dict] = []

        for entity in entities:
            points = getattr(entity, "points", None)

            if not points:
                continue

            for start, end in self._segments(entity):
                x1, y1 = float(start[0]), float(start[1])
                x2, y2 = float(end[0]), float(end[1])
                dx = x2 - x1
                dy = y2 - y1
                length = hypot(dx, dy)

                if length < 50.0:
                    continue

                if abs(dx) <= 0.001 or abs(dy) <= 0.001:
                    segments.append(
                        {
                            "x1": x1,
                            "y1": y1,
                            "x2": x2,
                            "y2": y2,
                            "length": length,
                            "orientation": (
                                "vertical"
                                if abs(dx) <= abs(dy)
                                else "horizontal"
                            ),
                        }
                    )

        return segments

    def _small_polyline_glyphs(self, entities: list) -> list[dict]:
        glyphs: list[dict] = []

        for entity in entities:
            if not isinstance(entity, DXFPolyline) or not entity.points:
                continue

            xs = [float(point[0]) for point in entity.points]
            ys = [float(point[1]) for point in entity.points]
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)

            if width <= 0.0 or height <= 0.0:
                continue

            if width > 8.0 or height > 8.0:
                continue

            if len(entity.points) < 5:
                continue

            glyphs.append(
                {
                    "entity": entity,
                    "min_x": min(xs),
                    "max_x": max(xs),
                    "min_y": min(ys),
                    "max_y": max(ys),
                    "width": width,
                    "height": height,
                    "center_x": (min(xs) + max(xs)) / 2.0,
                    "center_y": (min(ys) + max(ys)) / 2.0,
                    "point_count": len(entity.points),
                }
            )

        return glyphs

    def _read_glyphs_near_line(self, line: dict, glyphs: list[dict]) -> str | None:
        if line["orientation"] != "vertical":
            return None

        line_x = line["x1"]
        min_y = min(line["y1"], line["y2"])
        max_y = max(line["y1"], line["y2"])

        nearby = [
            glyph
            for glyph in glyphs
            if abs(glyph["center_x"] - line_x) <= 8.0
            and min_y <= glyph["center_y"] <= max_y
        ]

        if not nearby:
            return None

        groups = self._group_vertical_glyphs(nearby)
        digits = [
            self._classify_rotated_digit(group)
            for group in groups
        ]

        if any(digit is None for digit in digits):
            return None

        value_text = "".join(str(digit) for digit in digits)
        numeric_value = self._numeric_value(value_text)

        if len(value_text) < 2 or numeric_value in (None, 0.0):
            return None

        return value_text

    def _group_vertical_glyphs(self, glyphs: list[dict]) -> list[list[dict]]:
        groups: list[list[dict]] = []

        for glyph in sorted(glyphs, key=lambda item: item["center_y"]):
            if not groups:
                groups.append([glyph])
                continue

            previous = groups[-1]
            previous_max = max(item["max_y"] for item in previous)

            if glyph["min_y"] - previous_max <= 0.45:
                previous.append(glyph)
            else:
                groups.append([glyph])

        return groups

    def _classify_rotated_digit(self, group: list[dict]) -> int | None:
        min_x = min(item["min_x"] for item in group)
        max_x = max(item["max_x"] for item in group)
        min_y = min(item["min_y"] for item in group)
        max_y = max(item["max_y"] for item in group)
        width = max_x - min_x
        height = max_y - min_y
        polyline_count = len(group)
        max_points = max(item["point_count"] for item in group)

        if polyline_count >= 2 and max_points >= 15:
            return 0

        if polyline_count >= 2 and max_points < 15:
            return 4

        if polyline_count == 1 and width > height:
            return 1

        return None

    def _segments(self, entity: DXFPolyline):
        pairs = list(zip(entity.points, entity.points[1:]))

        if entity.closed and len(entity.points) > 1:
            pairs.append((entity.points[-1], entity.points[0]))

        return pairs

    def _drawing_from_source(self, source: Any):
        if hasattr(source, "modelspace") and hasattr(source, "header"):
            return source

        filename = self._filename_from_source(source)

        if filename is None:
            return None

        try:
            return ezdxf.readfile(str(filename))
        except Exception:  # noqa: BLE001 - detector reports unavailable source
            return None

    def _filename_from_source(self, source: Any) -> Path | None:
        if isinstance(source, (str, Path)):
            return Path(source)

        filename = getattr(source, "filename", "")

        if filename:
            return Path(filename)

        return None

    def _from_text(self, entity) -> DimensionCandidate:
        text = str(getattr(entity.dxf, "text", "")).strip()
        point = getattr(entity.dxf, "insert", None)

        return DimensionCandidate(
            value_text=text,
            position=self._point(point),
            entity_type="TEXT",
            numeric_value=self._numeric_value(text),
        )

    def _from_mtext(self, entity) -> DimensionCandidate:
        if hasattr(entity, "plain_text"):
            text = entity.plain_text()
        else:
            text = getattr(entity, "text", "")

        point = getattr(entity.dxf, "insert", None)

        return DimensionCandidate(
            value_text=str(text).strip(),
            position=self._point(point),
            entity_type="MTEXT",
            numeric_value=self._numeric_value(str(text)),
        )

    def _from_dimension(self, entity) -> DimensionCandidate:
        text = str(getattr(entity.dxf, "text", "") or "").strip()
        measured_length = self._measurement(entity)

        if text in ("", "<>") and measured_length is not None:
            text = f"{measured_length:.6g}"

        point = getattr(entity.dxf, "text_midpoint", None)

        return DimensionCandidate(
            value_text=text,
            position=self._point(point),
            entity_type="DIMENSION",
            associated_entity=getattr(entity.dxf, "geometry", None),
            measured_length=measured_length,
            numeric_value=self._numeric_value(text),
        )

    def _measurement(self, entity) -> float | None:
        try:
            return float(entity.get_measurement())
        except Exception:  # noqa: BLE001 - optional ezdxf capability
            return None

    def _numeric_value(self, text: str) -> float | None:
        match = self._NUMBER_RE.search(text)

        if match is None:
            return None

        try:
            return float(match.group(0).replace(",", "."))
        except ValueError:
            return None

    @staticmethod
    def _point(point: Any) -> Position:
        if point is None:
            return (0.0, 0.0)

        return (
            float(getattr(point, "x", 0.0)),
            float(getattr(point, "y", 0.0)),
        )
