"""
Base tool class for OpenHomePlanner.
"""

from __future__ import annotations

from core.preview import PreviewDefinition


class Tool:
    """
    Base class for every drawing tool.

    Every tool (selection, outlet, wall, cable...)
    inherits from this class.
    """

    NAME = "Tool"

    CURSOR = None

    def __init__(self, canvas):

        self.canvas = canvas

    # ---------------------------------------------------------

    def activate(self):
        """
        Called when the tool becomes active.
        """
        pass

    # ---------------------------------------------------------

    def deactivate(self):
        """
        Called when another tool replaces this one.
        """
        pass

    # ---------------------------------------------------------

    def preview_definition(self) -> PreviewDefinition | None:
        """
        Return the temporary preview needed by this tool.

        Tools only describe the preview. They never create or manipulate
        graphics items directly.
        """
        return None

    # ---------------------------------------------------------

    def mouse_press(self, event):
        """
        Mouse button pressed.
        """
        return False

    # ---------------------------------------------------------

    def mouse_release(self, event):
        """
        Mouse button released.
        """
        return False

    # ---------------------------------------------------------

    def mouse_move(self, event):
        """
        Mouse moved.
        """
        return False

    # ---------------------------------------------------------

    def mouse_double_click(self, event):
        """
        Double click.
        """
        return False

    # ---------------------------------------------------------

    def key_press(self, event):
        """
        Keyboard pressed.
        """
        return False

    # ---------------------------------------------------------

    def key_release(self, event):
        """
        Keyboard released.
        """
        return False

    # ---------------------------------------------------------

    def draw_overlay(self, painter):
        """
        Optional overlay drawing.

        Example:
            preview wall
            preview cable
            snap indicator
        """
        pass
