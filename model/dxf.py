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
    color_rgb: tuple[int, int, int] | None = None


# ==========================================================
# Layer
# ==========================================================

@dataclass
class DXFLayer:
    """
    DXF layer stored in the document model.

    This class intentionally contains no Qt dependency. The UI can toggle
    ``visible`` and the graphics layer can repaint from that model state.
    """

    name: str
    visible: bool = True
    locked: bool = False
    color: int = 7
    color_rgb: tuple[int, int, int] | None = None


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

    layers: dict[str, DXFLayer] = field(default_factory=dict)

    warnings: list[str] = field(default_factory=list)

    def ensure_layer(
        self,
        name: str,
        color: int = 7,
        color_rgb: tuple[int, int, int] | None = None,
        visible: bool = True,
        locked: bool = False,
    ) -> DXFLayer:
        """
        Return an existing layer or create it.

        Entities may reference layers that are absent from the DXF layer table,
        especially in imperfect exported files. Keeping this method in the
        model lets the importer stay simple and keeps layer consistency in one
        place.
        """

        if not name:
            name = "0"

        if name not in self.layers:
            self.layers[name] = DXFLayer(
                name=name,
                visible=visible,
                locked=locked,
                color=color,
                color_rgb=color_rgb,
            )
        else:
            layer = self.layers[name]
            if color is not None and layer.color == 7:
                layer.color = color
            if color_rgb is not None and layer.color_rgb is None:
                layer.color_rgb = color_rgb
            layer.visible = layer.visible and visible
            layer.locked = layer.locked or locked

        return self.layers[name]

    def set_layer_visible(
        self,
        name: str,
        visible: bool,
    ) -> None:
        """
        Change the visibility of a layer.
        """

        layer = self.ensure_layer(name)

        layer.visible = visible

    def is_layer_visible(
        self,
        name: str,
    ) -> bool:
        """
        Return True when a layer should be painted.
        """

        layer = self.layers.get(name)

        if layer is None:
            return True

        return layer.visible
