#!/usr/bin/env python3
"""
OpenHomePlanner

Main entry point.
"""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow
from importer.dxf_importer import DXFImporter


def main() -> int:
    """
    Application entry point.
    """

    app = QApplication(sys.argv)

    app.setApplicationName("OpenHomePlanner")
    app.setOrganizationName("OpenHomePlanner")

    window = MainWindow()

    doc = DXFImporter().load(
        r"rochette.dxf"
    )

    window.canvas.load_dxf(doc)
    window.showMaximized()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())