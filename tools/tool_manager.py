"""
Tool manager for OpenHomePlanner.
"""

from __future__ import annotations

from tools.tool import Tool


class ToolManager:
    """
    Holds the current active tool and forwards events to it.
    """

    def __init__(self, canvas):

        self.canvas = canvas

        self.current_tool: Tool | None = None

    # ---------------------------------------------------------

    def set_tool(self, tool: Tool):

        if self.current_tool is not None:
            self.current_tool.deactivate()

        self.current_tool = tool

        if self.current_tool is not None:
            self.current_tool.activate()

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