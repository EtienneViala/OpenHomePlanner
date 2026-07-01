"""
Main toolbar widgets.
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QToolBar


class MainToolBar(QToolBar):
    """
    Toolbar exposing user actions without owning application logic.
    """

    toolRequested = Signal(str)
    zoomInRequested = Signal()
    zoomOutRequested = Signal()
    fitRequested = Signal()
    snapToggled = Signal(bool)
    gridToggled = Signal(bool)

    def __init__(self, parent=None):

        super().__init__("Outils", parent)

        self.setMovable(False)

        self._build_actions()

    def _build_actions(self):

        self.tool_group = QActionGroup(self)
        self.tool_group.setExclusive(True)

        self.select_action = QAction("Sélection", self)
        self.select_action.setCheckable(True)
        self.select_action.triggered.connect(
            lambda: self.toolRequested.emit("select")
        )

        self.outlet_action = QAction("Prise", self)
        self.outlet_action.setCheckable(True)
        self.outlet_action.triggered.connect(
            lambda: self.toolRequested.emit("outlet")
        )

        self.wall_action = QAction("Mur", self)
        self.wall_action.setCheckable(True)
        self.wall_action.triggered.connect(
            lambda: self.toolRequested.emit("wall")
        )

        self.tool_group.addAction(self.select_action)
        self.tool_group.addAction(self.wall_action)
        self.tool_group.addAction(self.outlet_action)

        self.zoom_in_action = QAction("Zoom +", self)
        self.zoom_in_action.triggered.connect(self.zoomInRequested.emit)

        self.zoom_out_action = QAction("Zoom -", self)
        self.zoom_out_action.triggered.connect(self.zoomOutRequested.emit)

        self.fit_action = QAction("Ajuster au plan", self)
        self.fit_action.setShortcut("Ctrl+0")
        self.fit_action.triggered.connect(self.fitRequested.emit)

        self.snap_action = QAction("Snap", self)
        self.snap_action.setCheckable(True)
        self.snap_action.setChecked(True)
        self.snap_action.toggled.connect(self.snapToggled.emit)

        self.grid_action = QAction("Grille", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.toggled.connect(self.gridToggled.emit)

        self.addAction(self.select_action)
        self.addAction(self.wall_action)
        self.addAction(self.outlet_action)
        self.addSeparator()
        self.addAction(self.zoom_in_action)
        self.addAction(self.zoom_out_action)
        self.addAction(self.fit_action)
        self.addSeparator()
        self.addAction(self.snap_action)
        self.addAction(self.grid_action)

    def set_active_tool(self, tool_id: str):
        """
        Synchronize checked tool action with ToolManager.
        """
        actions = {
            "select": self.select_action,
            "wall": self.wall_action,
            "outlet": self.outlet_action,
        }

        action = actions.get(tool_id)

        if action is not None:
            action.setChecked(True)
