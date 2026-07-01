"""
Outlet placement tool.
"""

from PySide6.QtCore import Qt

from tools.tool import Tool
from model.electrical import Outlet


class OutletTool(Tool):

    TOOL_ID = "outlet"

    NAME = "Outlet"

    def mouse_press(self, event):

        if event.button() != Qt.LeftButton:
            return False

        scene_pos = self.canvas.snap_position(event)

        outlet = Outlet(
            x=scene_pos.x(),
            y=scene_pos.y(),
            name="Nouvelle prise"
        )

        self.canvas.project.add_object(outlet)

        return True
