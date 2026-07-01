"""
Tool manager for OpenHomePlanner.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal

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

    # ---------------------------------------------------------

    def set_tool(self, tool: Tool):

        if self.current_tool is not None:
            self.current_tool.deactivate()

        self.current_tool = tool

        if self.current_tool is not None:
            self.current_tool.activate()

            tool_id = getattr(self.current_tool, "TOOL_ID", "")
            tool_name = getattr(self.current_tool, "NAME", "Tool")
            self.toolChanged.emit(tool_id, tool_name)

    # ---------------------------------------------------------

    def mouse_press(self, event):

        if self.current_tool is None:
            return False

        return self.current_tool.mouse_press(event)

    # ---------------------------------------------------------

    def mouse_release(self, event):

        if self.current_tool is None:
            return False

        return self.current_tool.mouse_release(event)

    # ---------------------------------------------------------

    def mouse_move(self, event):

        if self.current_tool is None:
            return False

        return self.current_tool.mouse_move(event)

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
