"""
DXF model classes.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ==========================================================
# Base entity
# ==========================================================

@dataclass
class DXFEntity:
    layer: str = "0"
    color: int = 7


# ==========================================================
# Line
# ==========================================================

@dataclass
class DXFLine(DXFEntity):

    x1: float = 0.0
    y1: float = 0.0

    x2: float = 0.0
    y2: float = 0.0


# ==========================================================
# Circle
# ==========================================================

@dataclass
class DXFCircle(DXFEntity):

    x: float = 0.0
    y: float = 0.0

    radius: float = 1.0


# ==========================================================
# Polyline
# ==========================================================

@dataclass
class DXFPolyline(DXFEntity):

    points: list = field(default_factory=list)

    closed: bool = False


# ==========================================================
# Document
# ==========================================================

@dataclass
class DXFDocument:

    filename: str = ""

    entities: list = field(default_factory=list)