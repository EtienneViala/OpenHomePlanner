"""
OpenHomePlanner

Canvas principal.
"""

from pathlib import Path
from graphics.outlet_item import OutletItem
from model.electrical import Outlet
from graphics.factory import GraphicsFactory
from tools.tool_manager import ToolManager
from tools.select_tool import SelectTool
from graphics.dxf_item import DXFItem

from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
)


class Canvas(QGraphicsView):

    GRID_SIZE = 50

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.project.objects.connect(self.on_object_added)
        self.tool_manager = ToolManager(self)
        
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

        self.scene.selectionChanged.connect(
            self.on_selection_changed
        )

        self.tool_manager.set_tool(
            SelectTool(self)
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

    def mousePressEvent(self, event):

        if self.tool_manager.mouse_press(event):
            return

        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):

        if self.tool_manager.mouse_release(event):
            return

        super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):

        pos = self.mapToScene(event.position().toPoint())

        self.window().statusBar().showMessage(
            f"X : {pos.x():.0f}    Y : {pos.y():.0f}"
        )

        if self.tool_manager.mouse_move(event):
            return

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
    
    def add_outlet(self, x, y):

        outlet = Outlet(
            x=x,
            y=y,
            name="Prise"
        )

        item = OutletItem(outlet)

        self.scene.addItem(item)

        return item
    
    def on_object_added(self, obj):

        item = GraphicsFactory.create(obj)

        self.scene.addItem(item)

    def on_selection_changed(self):

        items = self.scene.selectedItems()

        if not items:

            self.project.selection.clear()

            return

        item = items[0]

        self.project.selection.set(
            item.object
        )

        from PySide6.QtCore import QPointF


    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    # ==========================================================
    # Utilities
    # ==========================================================

    def scene_position(self, event) -> QPointF:
        """
        Convert mouse event to scene coordinates.
        """
        return self.mapToScene(event.position().toPoint())


    # ----------------------------------------------------------

    def snap(self, point: QPointF) -> QPointF:
        """
        Snap a point to the current grid.
        """

        step = self.GRID_SIZE

        x = round(point.x() / step) * step
        y = round(point.y() / step) * step

        return QPointF(x, y)


    # ----------------------------------------------------------

    def snap_position(self, event) -> QPointF:
        """
        Mouse event -> snapped scene position.
        """
        return self.snap(
            self.scene_position(event)
        )
    
    def load_dxf(self, document):

        if hasattr(self, "_dxf_item"):

            self.scene.removeItem(
                self._dxf_item
            )

        self._dxf_item = DXFItem(document)

        #
        # Le DXF reste derrière
        #

        self._dxf_item.setZValue(-1000)

        self.scene.addItem(
            self._dxf_item
        )

        self.fitInView(
            self._dxf_item,
            Qt.KeepAspectRatio
        )