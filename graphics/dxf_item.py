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

    def __init__(self, document: DXFDocument):

        super().__init__()

        self.document = document

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
                    entity.x1,
                    -entity.y1
                )

                path.lineTo(
                    entity.x2,
                    -entity.y2
                )

            #
            # POLYLINE
            #

            elif isinstance(entity, DXFPolyline):

                if not entity.points:
                    continue

                x, y = entity.points[0]

                path.moveTo(
                    x,
                    -y
                )

                for x, y in entity.points[1:]:

                    path.lineTo(
                        x,
                        -y
                    )

                if entity.closed:

                    path.closeSubpath()

            #
            # CIRCLE
            #

            elif isinstance(entity, DXFCircle):

                r = entity.radius

                path.addEllipse(
                    entity.x-r,
                    -entity.y-r,
                    r*2,
                    r*2
                )

        self._update_bounding_rect()

    # ---------------------------------------------------------

    def _path_for_layer(self, layer_name):

        if layer_name not in self.paths_by_layer:

            self.paths_by_layer[layer_name] = QPainterPath()

        return self.paths_by_layer[layer_name]

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

        pen = QPen(
            QColor(180,180,180)
        )

        pen.setCosmetic(True)

        painter.setPen(pen)

        for layer_name, path in self.paths_by_layer.items():

            if not self.document.is_layer_visible(layer_name):

                continue

            painter.drawPath(
                path
            )
