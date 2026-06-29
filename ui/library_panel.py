"""
Library panel for OpenHomePlanner.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDockWidget,
    QTreeWidget,
    QTreeWidgetItem,
)


class LibraryPanel(QDockWidget):
    """
    Left library panel.

    Emits a signal when the user activates a tool.
    """

    toolSelected = Signal(str)

    def __init__(self):

        super().__init__("Library")

        self.tree = QTreeWidget()

        self.tree.setHeaderHidden(True)

        self.setWidget(self.tree)

        self._build_tree()

        self.tree.itemDoubleClicked.connect(
            self.on_item_double_clicked
        )

    # ---------------------------------------------------------

    def _build_tree(self):

        #
        # Selection
        #

        selection = QTreeWidgetItem(["Selection"])

        tool = QTreeWidgetItem(["🖱 Select"])

        tool.setData(
            0,
            Qt.UserRole,
            "select"
        )

        selection.addChild(tool)

        #
        # Electrical
        #

        electrical = QTreeWidgetItem(["Electrical"])

        outlet = QTreeWidgetItem(["🔌 Outlet"])

        outlet.setData(
            0,
            Qt.UserRole,
            "outlet"
        )

        switch = QTreeWidgetItem(["🔀 Switch"])

        switch.setData(
            0,
            Qt.UserRole,
            "switch"
        )

        light = QTreeWidgetItem(["💡 Light"])

        light.setData(
            0,
            Qt.UserRole,
            "light"
        )

        electrical.addChild(outlet)
        electrical.addChild(switch)
        electrical.addChild(light)

        #
        # Architecture
        #

        architecture = QTreeWidgetItem(["Architecture"])

        wall = QTreeWidgetItem(["🧱 Wall"])

        wall.setData(
            0,
            Qt.UserRole,
            "wall"
        )

        architecture.addChild(wall)

        #
        # Add to tree
        #

        self.tree.addTopLevelItem(selection)
        self.tree.addTopLevelItem(architecture)
        self.tree.addTopLevelItem(electrical)

        self.tree.expandAll()

    # ---------------------------------------------------------

    def on_item_double_clicked(self, item, column):

        tool = item.data(
            0,
            Qt.UserRole
        )

        if tool is None:
            return

        self.toolSelected.emit(tool)