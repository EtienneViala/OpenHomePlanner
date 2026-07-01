"""
Wall graphics item.
"""

from __future__ import annotations

from math import hypot

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem

from model.architecture import Wall


class WallItem(QGraphicsItem):
    """
    Permanent Qt representation of an architectural wall.
    """

    def __init__(self, wall: Wall):

        super().__init__()

        self.object = wall
        self._last_pos = QPointF(*wall.start)

        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setPos(self._last_pos)
        self.setZValue(100.0)

    def boundingRect(self):
        return self._wall_polygon().boundingRect().adjusted(
            -8.0,
            -8.0,
            8.0,
            8.0,
        )

    def paint(self, painter, option, widget):
        pen = QPen(QColor(185, 215, 225))
        pen.setWidth(0)

        if self.isSelected():
            pen.setColor(QColor("yellow"))

        painter.setPen(pen)
        painter.setBrush(QColor(90, 105, 110, 210))
        painter.drawPolygon(self._wall_polygon())

        axis_pen = QPen(QColor(230, 240, 245, 180))
        axis_pen.setWidth(0)
        painter.setPen(axis_pen)
        painter.setBrush(QColor(0, 0, 0, 0))

        dx = self.object.end[0] - self.object.start[0]
        dy = self.object.end[1] - self.object.start[1]
        painter.drawLine(QPointF(0.0, 0.0), QPointF(dx, dy))

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            dx = self.pos().x() - self._last_pos.x()
            dy = self.pos().y() - self._last_pos.y()

            if dx != 0.0 or dy != 0.0:
                self.object.move(dx, dy)
                self._last_pos = QPointF(self.pos())

        return super().itemChange(change, value)

    def _wall_polygon(self) -> QPolygonF:
        dx = self.object.end[0] - self.object.start[0]
        dy = self.object.end[1] - self.object.start[1]
        length = hypot(dx, dy)
        half = self.object.thickness / 2.0

        if length <= 0.0:
            return QPolygonF([
                QPointF(-half, -half),
                QPointF(half, -half),
                QPointF(half, half),
                QPointF(-half, half),
            ])

        nx = -dy / length
        ny = dx / length
        offset = QPointF(nx * half, ny * half)
        end = QPointF(dx, dy)

        return QPolygonF([
            offset,
            end + offset,
            end - offset,
            QPointF(-offset.x(), -offset.y()),
        ])
