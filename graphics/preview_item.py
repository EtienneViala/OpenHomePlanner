"""
Temporary graphics item used for placement previews.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen
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

    def boundingRect(self):
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
