"""
DXF layers panel.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDockWidget,
    QTreeWidget,
    QTreeWidgetItem,
)

from model.dxf import DXFDocument


class LayersPanel(QDockWidget):
    """
    Displays DXF layers and lets the user toggle their visibility.

    The panel only edits the DXF model and emits a signal. It does not access
    the canvas or any graphics item directly, which keeps the UI replaceable
    and preserves the model/view separation used by the project.
    """

    layerVisibilityChanged = Signal(str, bool)

    def __init__(self):

        super().__init__("Layers")

        self.document: DXFDocument | None = None
        self._updating = False

        self.tree = QTreeWidget()

        self.tree.setHeaderLabels([
            "Layer",
            "Entities",
        ])

        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)

        self.setWidget(self.tree)

        self.tree.itemChanged.connect(
            self.on_item_changed
        )

    # ---------------------------------------------------------

    def load_document(
        self,
        document: DXFDocument | None,
    ) -> None:
        """
        Display layers from the current DXF document.
        """

        self.document = document
        self._updating = True

        self.tree.clear()

        if document is None:

            self._updating = False

            return

        entity_counts = self._count_entities_by_layer(document)

        for layer_name in sorted(document.layers):

            layer = document.layers[layer_name]

            item = QTreeWidgetItem([
                layer.name,
                str(entity_counts.get(layer.name, 0)),
            ])

            item.setData(
                0,
                Qt.UserRole,
                layer.name,
            )

            item.setFlags(
                item.flags()
                | Qt.ItemIsUserCheckable
                | Qt.ItemIsEnabled
            )

            item.setCheckState(
                0,
                Qt.Checked if layer.visible else Qt.Unchecked,
            )

            self.tree.addTopLevelItem(item)

        self.tree.resizeColumnToContents(0)

        self._updating = False

    # ---------------------------------------------------------

    def _count_entities_by_layer(
        self,
        document: DXFDocument,
    ) -> dict[str, int]:
        """
        Count entities for user feedback without adding UI state to the model.
        """

        counts: dict[str, int] = {}

        for entity in document.entities:

            counts[entity.layer] = counts.get(
                entity.layer,
                0,
            ) + 1

        return counts

    # ---------------------------------------------------------

    def on_item_changed(
        self,
        item: QTreeWidgetItem,
        column: int,
    ) -> None:

        if self._updating or column != 0:

            return

        layer_name = item.data(
            0,
            Qt.UserRole,
        )

        visible = item.checkState(0) == Qt.Checked

        if self.document is not None:

            self.document.set_layer_visible(
                layer_name,
                visible,
            )

        self.layerVisibilityChanged.emit(
            layer_name,
            visible,
        )
