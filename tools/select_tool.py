"""
Selection tool.
"""

import logging

from tools.tool import Tool


logger = logging.getLogger(__name__)


class SelectTool(Tool):

    TOOL_ID = "select"

    NAME = "Selection"

    def activate(self):

        logger.debug("Selection tool activated")

    def deactivate(self):

        logger.debug("Selection tool deactivated")

    def mouse_press(self, event):

        # On laisse QGraphicsView gérer la sélection.
        return False
