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

        self.path = QPainterPath()

        self._build_path()

    # ---------------------------------------------------------

    def _build_path(self):

        for entity in self.document.entities:

            #
            # LINE
            #

            if isinstance(entity, DXFLine):

                self.path.moveTo(
                    entity.x1,
                    -entity.y1
                )

                self.path.lineTo(
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

                self.path.moveTo(
                    x,
                    -y
                )

                for x, y in entity.points[1:]:

                    self.path.lineTo(
                        x,
                        -y
                    )

                if entity.closed:

                    self.path.closeSubpath()

            #
            # CIRCLE
            #

            elif isinstance(entity, DXFCircle):

                r = entity.radius

                self.path.addEllipse(
                    entity.x-r,
                    -entity.y-r,
                    r*2,
                    r*2
                )

    # ---------------------------------------------------------

    def boundingRect(self):

        return self.path.boundingRect()

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

        painter.drawPath(
            self.path
        )