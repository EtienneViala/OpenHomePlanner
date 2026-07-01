"""
DXF graphics item.
"""

from PySide6.QtCore import QRectF
from PySide6.QtGui import (
    QColor,
    QPainterPath,
    QPen,
)

from PySide6.QtWidgets import QGraphicsItem

from model.dxf import (
    DXFDocument,
    DXFLine,
    DXFPolyline,
    DXFCircle,
)


class DXFItem(QGraphicsItem):

    def __init__(
        self,
        document: DXFDocument,
        scale_factor: float = 1.0,
    ):

        super().__init__()

        self.document = document
        self.scale_factor = scale_factor

        self.paths_by_layer = {}

        self._bounding_rect = QRectF()

        self._build_path()

    # ---------------------------------------------------------

    def _build_path(self):

        self.paths_by_layer.clear()

        for entity in self.document.entities:

            path = self._path_for_layer(entity.layer)

            #
            # LINE
            #

            if isinstance(entity, DXFLine):

                path.moveTo(
                    self._sx(entity.x1),
                    self._sy(entity.y1)
                )

                path.lineTo(
                    self._sx(entity.x2),
                    self._sy(entity.y2)
                )

            #
            # POLYLINE
            #

            elif isinstance(entity, DXFPolyline):

                if not entity.points:
                    continue

                x, y = entity.points[0]

                path.moveTo(
                    self._sx(x),
                    self._sy(y)
                )

                for x, y in entity.points[1:]:

                    path.lineTo(
                        self._sx(x),
                        self._sy(y)
                    )

                if entity.closed:

                    path.closeSubpath()

            #
            # CIRCLE
            #

            elif isinstance(entity, DXFCircle):

                r = entity.radius

                path.addEllipse(
                    self._sx(entity.x - r),
                    self._sy(entity.y + r),
                    self._scaled(r * 2),
                    self._scaled(r * 2)
                )

        self._update_bounding_rect()

    # ---------------------------------------------------------

    def _path_for_layer(self, layer_name):

        if layer_name not in self.paths_by_layer:

            self.paths_by_layer[layer_name] = QPainterPath()

        return self.paths_by_layer[layer_name]

    # ---------------------------------------------------------

    def _scaled(self, value):
        return value * self.scale_factor

    def _sx(self, value):
        return self._scaled(value)

    def _sy(self, value):
        return -self._scaled(value)

    # ---------------------------------------------------------

    def _update_bounding_rect(self):

        rect = QRectF()

        for path in self.paths_by_layer.values():

            if rect.isNull():

                rect = path.boundingRect()

            else:

                rect = rect.united(path.boundingRect())

        self._bounding_rect = rect

    # ---------------------------------------------------------

    def boundingRect(self):

        return self._bounding_rect

    # ---------------------------------------------------------

    def refresh_layers(self):
        """
        Repaint after layer visibility changed.

        Geometry is unchanged when a layer is shown or hidden, so we only need
        to schedule a repaint instead of rebuilding paths or reloading the DXF.
        """

        self.update()

    # ---------------------------------------------------------

    def paint(
        self,
        painter,
        option,
        widget
    ):

        for layer_name, path in self.paths_by_layer.items():

            if not self.document.is_layer_visible(layer_name):

                continue

            layer = self.document.layers.get(layer_name)
            color_rgb = None

            if layer is not None:
                color_rgb = layer.color_rgb

            if color_rgb is None:
                color_rgb = (180, 180, 180)

            pen = QPen(QColor(*color_rgb))
            pen.setCosmetic(True)
            painter.setPen(pen)

            painter.drawPath(
                path
            )
