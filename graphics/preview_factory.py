"""
Factory for temporary placement previews.
"""

from __future__ import annotations

from core.preview import PreviewDefinition
from graphics.preview_item import PreviewItem


class PreviewFactory:
    """
    Create graphics items used only for preview display.

    Preview items are deliberately separate from permanent project items. They
    are not stored in the project and do not carry business behavior.
    """

    @staticmethod
    def create(definition: PreviewDefinition) -> PreviewItem:
        return PreviewItem(definition)
