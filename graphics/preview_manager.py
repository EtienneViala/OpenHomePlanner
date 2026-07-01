"""
Manager for temporary placement preview items.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF

from core.preview import PreviewDefinition
from graphics.preview_factory import PreviewFactory


class PreviewManager:
    """
    Own the lifecycle of the current placement preview.

    The manager decides when to create or remove the temporary item. The canvas
    only displays, moves and removes the item it receives.
    """

    def __init__(self, canvas):

        self.canvas = canvas
        self._definition: PreviewDefinition | None = None
        self._item = None

    def set_preview(self, definition: PreviewDefinition | None) -> None:
        """
        Replace the active preview definition.
        """
        self.clear()
        self._definition = definition

    def move_to(self, position: QPointF) -> None:
        """
        Ensure the preview exists and move it to a scene position.
        """
        if self._definition is None:
            return

        if self._item is None:
            self._item = PreviewFactory.create(self._definition)
            self.canvas.show_preview_item(self._item)

        self.canvas.move_preview_item(position)

    def hide_item(self) -> None:
        """
        Remove the visible preview while keeping its definition active.
        """
        if self._item is None:
            return

        self.canvas.remove_preview_item()
        self._item = None

    def clear(self) -> None:
        """
        Remove the current preview item and forget its definition.
        """
        self.hide_item()
        self._definition = None
