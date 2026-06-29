"""
Selection tool.
"""

from tools.tool import Tool


class SelectTool(Tool):

    NAME = "Selection"

    def activate(self):

        print("[Tool] Selection activated")

    def deactivate(self):

        print("[Tool] Selection deactivated")

    def mouse_press(self, event):

        # On laisse QGraphicsView gérer la sélection.
        return False