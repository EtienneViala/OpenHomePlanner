"""
Property panel for OpenHomePlanner.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
)


class PropertyPanel(QDockWidget):
    """
    Displays and edits the properties of the selected object.
    """

    def __init__(self):

        super().__init__("Properties")

        self.table = QTableWidget()

        self.table.setColumnCount(2)

        self.table.setHorizontalHeaderLabels([
            "Property",
            "Value"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeToContents
        )

        self.table.verticalHeader().setVisible(False)

        self.table.setAlternatingRowColors(True)

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        self.setWidget(self.table)

    # ---------------------------------------------------------

    def clear_properties(self):

        self.table.setRowCount(0)

    # ---------------------------------------------------------

    def display_object(self, obj):

        self.clear_properties()

        if obj is None:
            return

        properties = {
            "Type": obj.__class__.__name__,
            "Name": getattr(obj, "name", ""),
            "X": getattr(obj, "x", 0),
            "Y": getattr(obj, "y", 0),
            "Rotation": getattr(obj, "rotation", 0),
            "Layer": getattr(obj, "layer", ""),
        }

        #
        # Ajoute automatiquement tous les autres attributs
        #

        for key, value in obj.__dict__.items():

            if key in properties:
                continue

            properties[key] = value

        self.table.setRowCount(len(properties))

        row = 0

        for key, value in properties.items():

            item_name = QTableWidgetItem(str(key))

            item_name.setFlags(
                Qt.ItemIsEnabled
            )

            item_value = QTableWidgetItem(str(value))

            self.table.setItem(
                row,
                0,
                item_name
            )

            self.table.setItem(
                row,
                1,
                item_value
            )

            row += 1