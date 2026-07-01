"""
Main application window.
"""

from pathlib import Path
import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from core.project import Project
from importer.dxf_importer import DXFImporter, DXFImportError
from tools.outlet_tool import OutletTool
from tools.select_tool import SelectTool
from tools.wall_tool import WallTool
from ui.canvas import Canvas
from ui.layers_panel import LayersPanel
from ui.library_panel import LibraryPanel
from ui.property_panel import PropertyPanel
from ui.statusbar import MainStatusBar
from ui.toolbar import MainToolBar


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Main window assembling the canvas, panels, menus and actions.
    """

    def __init__(self):

        super().__init__()

        self.project = Project()
        self.current_file = None

        self.setWindowTitle("OpenHomePlanner")
        self.resize(1600, 900)

        self._create_canvas()
        self._create_statusbar()
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_library()
        self._create_layers()
        self._create_properties()
        self._connect_signals()

        self.canvas.tool_manager.set_tool(
            SelectTool(self.canvas)
        )

    def _create_canvas(self):

        self.canvas = Canvas(self.project)
        self.setCentralWidget(self.canvas)

    def _create_statusbar(self):

        self.status = MainStatusBar(self)
        self.setStatusBar(self.status)

    def _create_actions(self):

        self.action_new = QAction("Nouveau", self)
        self.action_open_svg = QAction("Importer SVG", self)
        self.action_import_dxf = QAction("Importer un DXF...", self)
        self.action_save = QAction("Sauvegarder", self)
        self.action_exit = QAction("Quitter", self)
        self.action_about = QAction("A propos", self)

        self.action_new.setShortcut("Ctrl+N")
        self.action_import_dxf.setShortcut("Ctrl+O")
        self.action_save.setShortcut("Ctrl+S")
        self.action_exit.setShortcut("Ctrl+Q")

        self.action_import_dxf.triggered.connect(self.import_dxf)
        self.action_open_svg.triggered.connect(self.import_svg)
        self.action_exit.triggered.connect(self.close)
        self.action_about.triggered.connect(self.about)

    def _create_menu(self):

        menu = self.menuBar()

        file_menu = menu.addMenu("&Fichier")
        file_menu.addAction(self.action_new)
        file_menu.addSeparator()
        file_menu.addAction(self.action_import_dxf)
        file_menu.addAction(self.action_open_svg)
        file_menu.addAction(self.action_save)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)

        help_menu = menu.addMenu("&Aide")
        help_menu.addAction(self.action_about)

    def _create_toolbar(self):

        self.toolbar = MainToolBar(self)
        self.addToolBar(self.toolbar)

        self.toolbar.toolRequested.connect(self.activate_tool)
        self.toolbar.zoomInRequested.connect(self.canvas.zoom_in)
        self.toolbar.zoomOutRequested.connect(self.canvas.zoom_out)
        self.toolbar.fitRequested.connect(self.canvas.fit_to_content)
        self.toolbar.snapToggled.connect(self.canvas.set_snap_enabled)
        self.toolbar.gridToggled.connect(self.canvas.set_grid_visible)

    def _create_library(self):

        self.library = LibraryPanel()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.library)

    def _create_layers(self):

        self.layers = LayersPanel()
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layers)

    def _create_properties(self):

        self.properties = PropertyPanel()
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties)

    def _connect_signals(self):

        self.project.selection.connect(self.properties.display_object)
        self.canvas.dxfLoaded.connect(self.layers.load_document)
        self.library.toolSelected.connect(self.activate_tool)
        self.layers.layerVisibilityChanged.connect(
            self.canvas.set_dxf_layer_visible
        )

        self.canvas.mousePositionChanged.connect(self.status.set_position)
        self.canvas.snapChanged.connect(self.status.set_snap_enabled)
        self.canvas.zoomChanged.connect(self.status.set_zoom)
        self.canvas.tool_manager.toolChanged.connect(self.on_tool_changed)

    def import_dxf(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un DXF",
            "",
            "DXF (*.dxf)",
        )

        if not filename:
            return

        self._load_dxf_file(Path(filename))

    def _load_dxf_file(self, filename: Path):

        try:
            document = DXFImporter().load(str(filename))
        except DXFImportError as exc:
            logger.exception("DXF import failed")
            QMessageBox.warning(
                self,
                "Import DXF",
                str(exc),
            )
            return

        self.current_file = filename
        self.project.set_dxf_document(document)
        self.canvas.load_dxf(document)
        self.statusBar().showMessage(f"DXF importe : {filename}")

        if document.warnings:
            QMessageBox.warning(
                self,
                "Import DXF",
                "\n".join(document.warnings[:10]),
            )

    def import_svg(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un SVG",
            "",
            "SVG (*.svg)",
        )

        if not filename:
            return

        self.current_file = Path(filename)
        self.canvas.import_svg(self.current_file)
        self.statusBar().showMessage(str(self.current_file))

    def about(self):

        QMessageBox.information(
            self,
            "OpenHomePlanner",
            "OpenHomePlanner\n\nVersion 0.7.1",
        )

    def activate_tool(self, tool_name: str):

        if tool_name == "select":
            self.canvas.tool_manager.set_tool(
                SelectTool(self.canvas)
            )
        elif tool_name == "outlet":
            self.canvas.tool_manager.set_tool(
                OutletTool(self.canvas)
            )
        elif tool_name == "wall":
            self.canvas.tool_manager.set_tool(
                WallTool(self.canvas)
            )

    def on_tool_changed(self, tool_id: str, tool_name: str):

        self.toolbar.set_active_tool(tool_id)
        self.status.set_tool(tool_name)
