"""
OpenHomePlanner

Canvas principal.
"""

from pathlib import Path

from graphics.factory import GraphicsFactory
from tools.tool_manager import ToolManager
from tools.select_tool import SelectTool
from graphics.dxf_item import DXFItem

from PySide6.QtCore import QPointF
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QKeySequence, QPainter, QPen
from PySide6.QtSvgWidgets import QGraphicsSvgItem
from PySide6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QMenu,
)


class Canvas(QGraphicsView):

    dxfLoaded = Signal(object)
    mousePositionChanged = Signal(float, float)
    snapChanged = Signal(bool)
    gridVisibilityChanged = Signal(bool)
    zoomChanged = Signal(float)

    GRID_SIZE = 50

    def __init__(self, project):

        super().__init__()

        self.project = project
        self.project.objects.connect(self.on_object_added)
        self.project.objects.connect_removed(self.on_object_removed)
        self.tool_manager = ToolManager(self)
        self._items_by_object = {}
        self._preview_item = None
        self._snap_enabled = True
        self._grid_visible = True
        
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

        self.setFocusPolicy(Qt.StrongFocus)

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
        self.zoomChanged.emit(self._zoom)

    def zoom_in(self):
        """
        Zoom in from toolbar or shortcut action.
        """
        self._apply_zoom_factor(1.15)

    def zoom_out(self):
        """
        Zoom out from toolbar or shortcut action.
        """
        self._apply_zoom_factor(1 / 1.15)

    def _apply_zoom_factor(self, factor: float):
        self._zoom *= factor
        self.scale(factor, factor)
        self.zoomChanged.emit(self._zoom)

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

        self.mousePositionChanged.emit(pos.x(), pos.y())

        if self.tool_manager.mouse_move(event):
            return

        super().mouseMoveEvent(event)

    def contextMenuEvent(self, event):
        """
        Show object actions without mutating the scene directly.
        """
        item = self.itemAt(event.pos())
        obj = getattr(item, "object", None) if item is not None else None

        if obj is None:
            super().contextMenuEvent(event)
            return

        if not item.isSelected():
            self.scene.clearSelection()
            item.setSelected(True)

        menu = QMenu(self)
        delete_action = menu.addAction("Supprimer")
        properties_action = menu.addAction("Propriétés")

        chosen_action = menu.exec(event.globalPos())

        if chosen_action == delete_action:
            self.delete_selection()
        elif chosen_action == properties_action:
            self.project.selection.set(obj)

    def keyPressEvent(self, event):
        """
        Canvas keyboard shortcuts.
        """
        if event.key() == Qt.Key_Escape:
            self.tool_manager.set_tool(SelectTool(self))
            event.accept()
            return

        if event.key() == Qt.Key_Delete:
            self.delete_selection()
            event.accept()
            return

        if event.matches(QKeySequence.SelectAll):
            self.select_all_objects()
            event.accept()
            return

        if (
            event.key() == Qt.Key_0
            and event.modifiers() & Qt.ControlModifier
        ):
            self.fit_to_content()
            event.accept()
            return

        if self.tool_manager.key_press(event):
            event.accept()
            return

        super().keyPressEvent(event)

    # ==========================================================
    # Background
    # ==========================================================

    def drawBackground(self, painter, rect):

        painter.fillRect(
            rect,
            QColor(35, 35, 35)
        )

        if not self._grid_visible:
            return

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
    
    def on_object_added(self, obj):

        item = GraphicsFactory.create(obj)

        self._items_by_object[obj.uid] = item

        self.scene.addItem(item)

    def on_object_removed(self, obj):

        item = self._items_by_object.pop(obj.uid, None)

        if item is not None:
            self.scene.removeItem(item)

    def show_preview_item(self, item):
        """
        Display a temporary preview item.
        """
        if self._preview_item is not None:
            self.remove_preview_item()

        self._preview_item = item
        self.scene.addItem(item)

    def move_preview_item(self, position: QPointF):
        """
        Move the visible temporary preview item.
        """
        if self._preview_item is None:
            return

        self._preview_item.setPos(position)

    def remove_preview_item(self):
        """
        Remove the visible temporary preview item.
        """
        if self._preview_item is None:
            return

        self.scene.removeItem(self._preview_item)
        self._preview_item = None

    def on_selection_changed(self):

        items = self.scene.selectedItems()

        if not items:

            self.project.selection.clear()

            return

        item = items[0]

        selected_object = getattr(item, "object", None)

        if selected_object is None:
            self.project.selection.clear()
            return

        self.project.selection.set(selected_object)

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
        Return the point snapped to the grid when snap is enabled.
        """
        if not self._snap_enabled:
            return point

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

    @property
    def snap_enabled(self) -> bool:
        return self._snap_enabled

    def set_snap_enabled(self, enabled: bool):
        self._snap_enabled = enabled
        self.snapChanged.emit(enabled)

    def toggle_snap(self):
        self.set_snap_enabled(not self._snap_enabled)

    @property
    def grid_visible(self) -> bool:
        return self._grid_visible

    def set_grid_visible(self, visible: bool):
        self._grid_visible = visible
        self.gridVisibilityChanged.emit(visible)
        self.viewport().update()

    def toggle_grid(self):
        self.set_grid_visible(not self._grid_visible)

    def selected_project_objects(self):
        objects = []

        for item in self.scene.selectedItems():
            obj = getattr(item, "object", None)
            if obj is not None:
                objects.append(obj)

        return objects

    def delete_selection(self):
        """
        Delete selected project objects through the project API.
        """
        objects = self.selected_project_objects()

        if not objects:
            return

        self.tool_manager.delete_objects(objects)

        self.scene.clearSelection()
        self.project.selection.clear()

    def select_all_objects(self):
        """
        Select every graphics item linked to a project object.
        """
        for item in self._items_by_object.values():
            item.setSelected(True)

    def fit_to_content(self):
        """
        Fit the view to the visible content of the scene.
        """
        rect = self.scene.itemsBoundingRect()

        if rect.isNull() or rect.isEmpty():
            return

        margin = 100
        rect = rect.adjusted(-margin, -margin, margin, margin)

        self.fitInView(rect, Qt.KeepAspectRatio)
        self._zoom = self.transform().m11()
        self.zoomChanged.emit(self._zoom)
    
    def load_dxf(
        self,
        document,
        scale_factor: float = 1.0,
    ):

        if hasattr(self, "_dxf_item"):

            self.scene.removeItem(
                self._dxf_item
            )

        self.dxf_document = document

        self._dxf_item = DXFItem(
            document,
            scale_factor=scale_factor,
        )

        #
        # Le DXF reste derrière
        #

        self._dxf_item.setZValue(-1000)

        self.scene.addItem(
            self._dxf_item
        )

        self.fit_to_content()

        self.dxfLoaded.emit(document)

    # ----------------------------------------------------------

    def set_dxf_layer_visible(
        self,
        layer_name: str,
        visible: bool,
    ) -> None:
        """
        Show or hide a DXF layer without reloading the file.
        """

        if not hasattr(self, "dxf_document"):

            return

        self.dxf_document.set_layer_visible(
            layer_name,
            visible,
        )

        if hasattr(self, "_dxf_item"):

            self._dxf_item.refresh_layers()
