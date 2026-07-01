"""
OpenHomePlanner

Main application window.
"""

from pathlib import Path
import logging

from core.project import Project
from importer.dxf_importer import DXFImporter, DXFImportError
from ui.property_panel import PropertyPanel
from ui.library_panel import LibraryPanel
from ui.layers_panel import LayersPanel
from tools.select_tool import SelectTool
from tools.outlet_tool import OutletTool

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QToolBar,
)

from ui.canvas import Canvas


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.project = Project()

        self.setWindowTitle("OpenHomePlanner")
        self.resize(1600, 900)

        self.current_file = None

        self._create_canvas()
        self._create_actions()
        self._create_menu()
        self._create_toolbar()
        self._create_library()
        self._create_layers()
        self._create_properties()

        self.project.selection.connect(
            self.properties.display_object
        )

        self.canvas.dxfLoaded.connect(
            self.layers.load_document
        )

        self.statusBar().showMessage("Ready")

        self.canvas.tool_manager.set_tool(
            SelectTool(self.canvas)
        )

    # ==============================================================
    # Canvas
    # ==============================================================

    def _create_canvas(self):

        self.canvas = Canvas(self.project)

        self.setCentralWidget(self.canvas)

    # ==============================================================
    # Actions
    # ==============================================================

    def _create_actions(self):

        self.action_new = QAction("Nouveau", self)

        self.action_open_svg = QAction("Importer SVG", self)

        self.action_import_dxf = QAction("Importer un DXF...", self)

        self.action_save = QAction("Sauvegarder", self)

        self.action_exit = QAction("Quitter", self)

        self.action_about = QAction("À propos", self)

        self.action_new.setShortcut("Ctrl+N")

        self.action_import_dxf.setShortcut("Ctrl+O")

        self.action_save.setShortcut("Ctrl+S")

        self.action_exit.setShortcut("Ctrl+Q")

        self.action_import_dxf.triggered.connect(self.import_dxf)

        self.action_open_svg.triggered.connect(self.import_svg)

        self.action_exit.triggered.connect(self.close)

        self.action_about.triggered.connect(self.about)

    # ==============================================================
    # Menu
    # ==============================================================

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

    # ==============================================================
    # Toolbar
    # ==============================================================

    def _create_toolbar(self):

        toolbar = QToolBar("Main")

        toolbar.setMovable(False)

        self.addToolBar(toolbar)

        toolbar.addAction(self.action_new)

        toolbar.addAction(self.action_import_dxf)

        toolbar.addAction(self.action_open_svg)

        toolbar.addAction(self.action_save)

        toolbar.addSeparator()

        toolbar.addAction("Sélection")

        toolbar.addAction("Mur")

        toolbar.addAction("Prise")

        toolbar.addAction("Interrupteur")

        toolbar.addAction("Lumière")

        toolbar.addAction("Câble")

    # ==============================================================
    # Library
    # ==============================================================

    def _create_library(self):

        self.library = LibraryPanel()

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.library
        )

        self.library.toolSelected.connect(
            self.on_tool_selected
        )

    # ==============================================================
    # Layers
    # ==============================================================

    def _create_layers(self):

        self.layers = LayersPanel()

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.layers
        )

        self.layers.layerVisibilityChanged.connect(
            self.canvas.set_dxf_layer_visible
        )

    # ==============================================================
    # Properties
    # ==============================================================

    def _create_properties(self):

        self.properties = PropertyPanel()

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            self.properties
        )

    # ==============================================================
    # DXF
    # ==============================================================

    def import_dxf(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un DXF",
            "",
            "DXF (*.dxf)"
        )

        if not filename:
            return

        self._load_dxf_file(Path(filename))

    # --------------------------------------------------------------

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
        self.canvas.load_dxf(document)

        self.statusBar().showMessage(
            f"DXF importé : {filename}"
        )

        if document.warnings:
            QMessageBox.warning(
                self,
                "Import DXF",
                "\n".join(document.warnings[:10]),
            )

    # ==============================================================
    # SVG
    # ==============================================================

    def import_svg(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Importer un SVG",
            "",
            "SVG (*.svg)"
        )

        if not filename:
            return

        self.current_file = Path(filename)

        self.canvas.import_svg(self.current_file)

        self.statusBar().showMessage(str(self.current_file))

    # ==============================================================
    # About
    # ==============================================================

    def about(self):

        QMessageBox.information(
            self,
            "OpenHomePlanner",
            "OpenHomePlanner\n\nVersion 0.6"
        )

    def on_tool_selected(self, tool_name):

        if tool_name == "select":

            self.canvas.tool_manager.set_tool(
                SelectTool(self.canvas)
            )

            self.statusBar().showMessage(
                "Selection tool"
            )

        elif tool_name == "outlet":

            self.canvas.tool_manager.set_tool(
                OutletTool(self.canvas)
            )

            self.statusBar().showMessage(
                "Outlet tool"
            )
