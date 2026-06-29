"""
OpenHomePlanner

Canvas principal.
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
)


class Canvas(QGraphicsView):

    GRID_SIZE = 50

    def __init__(self):

        super().__init__()

        self.scene = QGraphicsScene()

        self.scene.setSceneRect(
            -10000,
            -10000,
            20000,
            20000,
        )

        self.setScene(self.scene)

        self.setRenderHint(QPainter.Antialiasing)

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setViewportUpdateMode(
            QGraphicsView.FullViewportUpdate
        )

        self.setDragMode(
            QGraphicsView.ScrollHandDrag
        )

        self.setMouseTracking(True)

        self._zoom = 1.0

    # ==========================================================
    # SVG
    # ==========================================================

    def import_svg(self, filename: Path):

        item = QGraphicsSvgItem(str(filename))

        item.setFlag(
            item.GraphicsItemFlag.ItemIsSelectable,
            True,
        )

        self.scene.addItem(item)

    # ==========================================================
    # Zoom
    # ==========================================================

    def wheelEvent(self, event):

        if event.angleDelta().y() > 0:

            factor = 1.15

        else:

            factor = 1 / 1.15

        self._zoom *= factor

        self.scale(factor, factor)

    # ==========================================================
    # Mouse
    # ==========================================================

    def mouseMoveEvent(self, event):

        pos = self.mapToScene(
            event.position().toPoint()
        )

        window = self.window()

        window.statusBar().showMessage(
            f"X : {pos.x():.0f}    Y : {pos.y():.0f}"
        )

        super().mouseMoveEvent(event)

    # ==========================================================
    # Background
    # ==========================================================

    def drawBackground(self, painter, rect):

        painter.fillRect(
            rect,
            QColor(35, 35, 35)
        )

        pen = QPen(
            QColor(55, 55, 55)
        )

        pen.setWidth(0)

        painter.setPen(pen)

        left = int(rect.left())
        right = int(rect.right())

        top = int(rect.top())
        bottom = int(rect.bottom())

        x = left - (left % self.GRID_SIZE)

        while x <= right:

            painter.drawLine(
                x,
                top,
                x,
                bottom
            )

            x += self.GRID_SIZE

        y = top - (top % self.GRID_SIZE)

        while y <= bottom:

            painter.drawLine(
                left,
                y,
                right,
                y
            )

            y += self.GRID_SIZE