"""
Main application window.
"""

from pathlib import Path
import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from analysis.analyzer import BuildingAnalyzer
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
        self.action_detect_walls = QAction("Detecter les murs", self)
        self.action_clear_detected_walls = QAction(
            "Effacer les murs detectes",
            self,
        )
        self.action_redetect_walls = QAction("Redetecter les murs", self)
        self.action_exit = QAction("Quitter", self)
        self.action_about = QAction("A propos", self)

        self.action_new.setShortcut("Ctrl+N")
        self.action_import_dxf.setShortcut("Ctrl+O")
        self.action_save.setShortcut("Ctrl+S")
        self.action_exit.setShortcut("Ctrl+Q")

        self.action_import_dxf.triggered.connect(self.import_dxf)
        self.action_open_svg.triggered.connect(self.import_svg)
        self.action_detect_walls.triggered.connect(self.detect_walls)
        self.action_clear_detected_walls.triggered.connect(
            self.clear_detected_walls
        )
        self.action_redetect_walls.triggered.connect(self.redetect_walls)
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

        analysis_menu = menu.addMenu("&Analyse")
        analysis_menu.addAction(self.action_detect_walls)
        analysis_menu.addAction(self.action_clear_detected_walls)
        analysis_menu.addAction(self.action_redetect_walls)

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

        report = BuildingAnalyzer().analyze(filename)
        self.project.set_analysis_report(report)

        scale_factor = (
            report.scale_factor
            if report.scale_factor is not None
            else 1.0
        )

        self.canvas.load_dxf(
            document,
            scale_factor=scale_factor,
        )
        self.statusBar().showMessage(
            f"DXF importe : {filename} - echelle {scale_factor:.4f} "
            f"{report.real_unit}/DXF"
        )

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

    def detect_walls(self):
        """
        Run wall detection on the already loaded DXF and add walls to Project.
        """
        self._run_wall_detection(clear_existing=False)

    def clear_detected_walls(self):
        """
        Remove only automatically detected walls.
        """
        removed = self.project.remove_detected_walls()
        message = f"{removed} murs detectes effaces"
        self.statusBar().showMessage(message)
        QMessageBox.information(
            self,
            "Detection des murs",
            message,
        )

    def redetect_walls(self):
        """
        Replace previous detected walls with a fresh detection.
        """
        self._run_wall_detection(clear_existing=True)

    def _run_wall_detection(self, clear_existing: bool):
        if self.project.dxf_document is None:
            QMessageBox.information(
                self,
                "Detection des murs",
                "Importez d'abord un DXF.",
            )
            return

        removed = 0

        if clear_existing:
            removed = self.project.remove_detected_walls()

        report = BuildingAnalyzer().analyze(self.project.dxf_document)
        self.project.set_analysis_report(report)

        for wall in report.detected_walls:
            self.project.add_object(wall)

        message = self._analysis_summary_message(report, removed)
        self.statusBar().showMessage(message)
        QMessageBox.information(
            self,
            "Detection des murs",
            message,
        )

    def _analysis_summary_message(self, report, removed: int = 0) -> str:
        lines = []

        if removed:
            lines.append(f"Anciens murs detectes effaces : {removed}")

        lines.extend([
            f"Segments analyses : {report.segments_analyzed}",
            f"Segments ignores : {report.segments_ignored}",
            f"Murs detectes : {report.wall_count}",
            f"Doublons supprimes : {report.duplicates_removed}",
            f"Confiance moyenne : {report.average_wall_confidence:.2f}",
        ])

        return "\n".join(lines)

    def about(self):

        QMessageBox.information(
            self,
            "OpenHomePlanner",
            "OpenHomePlanner\n\nVersion 0.7.4",
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
