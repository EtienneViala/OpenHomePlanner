"""
Tool manager for OpenHomePlanner.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

from graphics.preview_manager import PreviewManager
from tools.tool import Tool


class ToolManager(QObject):
    """
    Holds the current active tool and forwards events to it.
    """

    toolChanged = Signal(str, str)

    def __init__(self, canvas):

        super().__init__()

        self.canvas = canvas

        self.current_tool: Tool | None = None
        self.preview = PreviewManager(canvas)

    # ---------------------------------------------------------

    def set_tool(self, tool: Tool):

        if self.current_tool is not None:
            self.current_tool.deactivate()

        self.preview.clear()
        self.current_tool = tool

        if self.current_tool is not None:
            self.current_tool.activate()
            self.preview.set_preview(
                self.current_tool.preview_definition()
            )

            tool_id = getattr(self.current_tool, "TOOL_ID", "")
            tool_name = getattr(self.current_tool, "NAME", "Tool")
            self.toolChanged.emit(tool_id, tool_name)

    # ---------------------------------------------------------

    def mouse_press(self, event):

        if self.current_tool is None:
            return False

        handled = self.current_tool.mouse_press(event)

        self.preview.set_preview(
            self.current_tool.preview_definition()
        )

        if handled and not self.current_tool.keep_preview_after_press():
            self.preview.hide_item()

        return handled

    # ---------------------------------------------------------

    def mouse_release(self, event):

        if self.current_tool is None:
            return False

        return self.current_tool.mouse_release(event)

    # ---------------------------------------------------------

    def mouse_move(self, event):

        if self.current_tool is None:
            return False

        handled = self.current_tool.mouse_move(event)
        snapped_position = self.canvas.snap_position(event)

        self.preview.set_preview(
            self.current_tool.preview_definition()
        )
        self.preview.move_to(
            self.current_tool.preview_position(snapped_position)
        )

        return handled

    # ---------------------------------------------------------

    def mouse_double_click(self, event):

        if self.current_tool is None:
            return False

        return self.current_tool.mouse_double_click(event)

    # ---------------------------------------------------------

    def key_press(self, event):

        if self.current_tool is None:
            return False

        return self.current_tool.key_press(event)

    # ---------------------------------------------------------

    def key_release(self, event):

        if self.current_tool is None:
            return False

        return self.current_tool.key_release(event)

    # ---------------------------------------------------------

    def delete_objects(self, objects):
        """
        Delete project objects through the project entry point.
        """
        for obj in objects:
            self.canvas.project.remove_object(obj)
