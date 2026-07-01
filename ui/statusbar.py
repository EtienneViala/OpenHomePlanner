"""
Permanent status bar for OpenHomePlanner.
"""

from PySide6.QtWidgets import QLabel, QStatusBar


class MainStatusBar(QStatusBar):
    """
    Shows canvas and tool state continuously.
    """

    def __init__(self, parent=None):

        super().__init__(parent)

        self.tool_label = QLabel("Outil : Sélection")
        self.position_label = QLabel("X : 0    Y : 0")
        self.snap_label = QLabel("Snap : ON")
        self.zoom_label = QLabel("Zoom : 100%")

        for label in (
            self.tool_label,
            self.position_label,
            self.snap_label,
            self.zoom_label,
        ):
            self.addPermanentWidget(label)

    def set_tool(self, tool_name: str):

        self.tool_label.setText(f"Outil : {tool_name}")

    def set_position(self, x: float, y: float):

        self.position_label.setText(f"X : {x:.0f}    Y : {y:.0f}")

    def set_snap_enabled(self, enabled: bool):

        self.snap_label.setText(
            f"Snap : {'ON' if enabled else 'OFF'}"
        )

    def set_zoom(self, zoom: float):

        self.zoom_label.setText(f"Zoom : {zoom * 100:.0f}%")
