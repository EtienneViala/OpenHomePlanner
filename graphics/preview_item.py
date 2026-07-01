"""
Temporary graphics item used for placement previews.
"""

from __future__ import annotations

from math import hypot

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem

from core.preview import PreviewDefinition


class PreviewItem(QGraphicsItem):
    """
    Semi-transparent item displayed while a placement tool follows the mouse.

    The item is not linked to a project object and cannot be selected or moved
    by the user. It is removed as soon as the active tool no longer needs it.
    """

    def __init__(self, definition: PreviewDefinition):

        super().__init__()

        self.definition = definition
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setOpacity(definition.opacity)
        self.setZValue(definition.z_value)

    def set_definition(self, definition: PreviewDefinition) -> None:
        """
        Replace preview data without recreating the scene item.
        """
        self.prepareGeometryChange()
        self.definition = definition
        self.setOpacity(definition.opacity)
        self.update()

    def boundingRect(self):
        if self.definition.shape == "wall":
            polygon = self._wall_polygon()
            rect = polygon.boundingRect()
            return rect.adjusted(-80.0, -80.0, 80.0, 80.0)

        size = self.definition.size

        return QRectF(
            -size / 2,
            -size / 2,
            size,
            size,
        )

    def paint(self, painter, option, widget):
        line_color = QColor(*self.definition.line_color)
        fill_color = QColor(*self.definition.fill_color)

        pen = QPen(line_color)
        pen.setWidth(2)

        painter.setPen(pen)
        painter.setBrush(fill_color)

        if self.definition.shape == "wall":
            self._paint_wall(painter, line_color, fill_color)
            return

        rect = self.boundingRect().adjusted(2, 2, -2, -2)

        if self.definition.shape == "circle_cross":
            painter.drawEllipse(rect)
            painter.drawLine(
                rect.center().x(),
                rect.top() + 4,
                rect.center().x(),
                rect.bottom() - 4,
            )
            painter.drawLine(
                rect.left() + 4,
                rect.center().y(),
                rect.right() - 4,
                rect.center().y(),
            )
            return

        if self.definition.shape == "circle":
            painter.drawEllipse(rect)
            return

        painter.drawRect(rect)

    def _wall_polygon(self) -> QPolygonF:
        definition = self.definition

        if definition.start is None or definition.end is None:
            return QPolygonF()

        start = QPointF(0.0, 0.0)
        dx = definition.end[0] - definition.start[0]
        dy = definition.end[1] - definition.start[1]
        length = hypot(dx, dy)

        if length <= 0.0:
            half = definition.thickness / 2.0
            return QPolygonF([
                QPointF(-half, -half),
                QPointF(half, -half),
                QPointF(half, half),
                QPointF(-half, half),
            ])

        nx = -dy / length
        ny = dx / length
        half = definition.thickness / 2.0
        end = QPointF(dx, dy)
        offset = QPointF(nx * half, ny * half)

        return QPolygonF([
            start + offset,
            end + offset,
            end - offset,
            start - offset,
        ])

    def _paint_wall(self, painter, line_color: QColor, fill_color: QColor) -> None:
        polygon = self._wall_polygon()

        pen = QPen(line_color)
        pen.setWidth(0)
        painter.setPen(pen)
        painter.setBrush(fill_color)
        painter.drawPolygon(polygon)

        if self.definition.start is None or self.definition.end is None:
            return

        dx = self.definition.end[0] - self.definition.start[0]
        dy = self.definition.end[1] - self.definition.start[1]

        center = QPointF(dx / 2.0, dy / 2.0)
        label = (
            f"L {self.definition.length:.0f} cm  "
            f"A {self.definition.angle:.1f} deg  "
            f"E {self.definition.thickness:.0f} cm"
        )

        painter.setPen(QPen(QColor(230, 240, 245)))
        painter.setFont(QFont("Arial", 10))

        path = QPainterPath()
        path.addText(center + QPointF(8.0, -8.0), painter.font(), label)
        painter.drawPath(path)
