"""
DXF unit detector.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import ezdxf


@dataclass(frozen=True)
class UnitDetection:
    """
    Normalized unit detection result.
    """

    unit: str
    confidence: float
    source: str = ""
    raw_code: int | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "unit": self.unit,
            "confidence": self.confidence,
            "source": self.source,
            "raw_code": self.raw_code,
            "warnings": list(self.warnings),
        }


class UnitDetector:
    """
    Detect drawing units from DXF metadata.
    """

    _INSUNITS = {
        1: "in",
        4: "mm",
        5: "cm",
        6: "m",
    }

    def detect(self, source: Any) -> UnitDetection:
        """
        Return a normalized unit from a DXF path, ezdxf drawing or header dict.
        """
        raw_code = self._read_insunits(source)

        if raw_code in self._INSUNITS:
            return UnitDetection(
                unit=self._INSUNITS[raw_code],
                confidence=0.9,
                source="$INSUNITS",
                raw_code=raw_code,
            )

        warning = "Unite DXF absente ou non supportee."

        return UnitDetection(
            unit="unknown",
            confidence=0.0,
            source="$INSUNITS",
            raw_code=raw_code,
            warnings=[warning],
        )

    def _read_insunits(self, source: Any) -> int | None:
        if isinstance(source, dict):
            return self._as_int(source.get("$INSUNITS"))

        header = getattr(source, "header", None)

        if header is not None:
            return self._as_int(header.get("$INSUNITS"))

        filename = self._filename_from_source(source)

        if filename is None:
            return None

        try:
            drawing = ezdxf.readfile(str(filename))
        except Exception:  # noqa: BLE001 - detector reports unknown units
            return None

        return self._as_int(drawing.header.get("$INSUNITS"))

    def _filename_from_source(self, source: Any) -> Path | None:
        if isinstance(source, (str, Path)):
            return Path(source)

        filename = getattr(source, "filename", "")

        if filename:
            return Path(filename)

        return None

    @staticmethod
    def _as_int(value: Any) -> int | None:
        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

