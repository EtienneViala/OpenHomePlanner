from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView
)


class Canvas(QGraphicsView):

    GRID = 50

    def __init__(self):

        super().__init__()

        self.scene = QGraphicsScene(-5000, -5000, 10000, 10000)

        self.setScene(self.scene)

        self.setRenderHints(
            QPainter.Antialiasing |
            QPainter.TextAntialiasing
        )

        self.setViewportUpdateMode(
            QGraphicsView.FullViewportUpdate
        )

        self.setDragMode(QGraphicsView.NoDrag)

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.AnchorUnderMouse
        )

        self.middle_pressed = False

    def wheelEvent(self, event):

        if event.angleDelta().y() > 0:
            self.scale(1.15, 1.15)
        else:
            self.scale(0.87, 0.87)

    def mousePressEvent(self, event):

        if event.button() == Qt.MiddleButton:

            self.middle_pressed = True

            self.setDragMode(QGraphicsView.ScrollHandDrag)

            fake = event

            super().mousePressEvent(fake)

            return

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MiddleButton:

            self.middle_pressed = False

            self.setDragMode(QGraphicsView.NoDrag)

        super().mouseReleaseEvent(event)

    def drawBackground(self, painter, rect):

        super().drawBackground(painter, rect)

        left = int(rect.left()) - (int(rect.left()) % self.GRID)
        top = int(rect.top()) - (int(rect.top()) % self.GRID)

        pen = QPen(QColor(60, 60, 60))
        pen.setWidth(0)

        painter.setPen(pen)

        x = left

        while x < rect.right():

            painter.drawLine(x, rect.top(), x, rect.bottom())

            x += self.GRID

        y = top

        while y < rect.bottom():

            painter.drawLine(rect.left(), y, rect.right(), y)

            y += self.GRID