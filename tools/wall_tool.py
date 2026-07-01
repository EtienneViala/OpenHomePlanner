"""
Manual wall drawing tool.
"""

from __future__ import annotations

from math import atan2, degrees, hypot

from PySide6.QtCore import QPointF, Qt

from core.preview import PreviewDefinition
from model.architecture import DEFAULT_WALL_THICKNESS, Wall
from tools.tool import Tool


class WallTool(Tool):
    """
    Create an architectural wall with two clicks.
    """

    TOOL_ID = "wall"
    NAME = "Wall"

    def __init__(self, canvas):
        super().__init__(canvas)
        self._start: QPointF | None = None
        self._current: QPointF | None = None
        self.thickness = DEFAULT_WALL_THICKNESS

    def deactivate(self):
        self._start = None
        self._current = None

    def preview_definition(self) -> PreviewDefinition | None:
        if self._start is None or self._current is None:
            return None

        length = hypot(
            self._current.x() - self._start.x(),
            self._current.y() - self._start.y(),
        )
        angle = degrees(
            atan2(
                self._current.y() - self._start.y(),
                self._current.x() - self._start.x(),
            )
        )

        return PreviewDefinition(
            shape="wall",
            line_color=(0, 220, 255),
            fill_color=(70, 95, 105),
            opacity=0.65,
            start=(self._start.x(), self._start.y()),
            end=(self._current.x(), self._current.y()),
            thickness=self.thickness,
            length=length,
            angle=angle,
        )

    def preview_position(self, snapped_position):
        if self._start is None:
            return snapped_position

        return self._start

    def keep_preview_after_press(self) -> bool:
        return self._start is not None

    def mouse_press(self, event):
        if event.button() != Qt.LeftButton:
            return False

        position = self.canvas.snap_position(event)

        if self._start is None:
            self._start = position
            self._current = position
            return True

        if self._is_too_short(self._start, position):
            self._current = position
            return True

        wall = Wall(
            name="Nouveau mur",
            start=(self._start.x(), self._start.y()),
            end=(position.x(), position.y()),
            thickness=self.thickness,
            orientation=degrees(
                atan2(
                    position.y() - self._start.y(),
                    position.x() - self._start.x(),
                )
            ),
        )

        self.canvas.project.add_object(wall)

        self._start = None
        self._current = None

        return True

    def mouse_move(self, event):
        if self._start is None:
            return False

        self._current = self.canvas.snap_position(event)
        return True

    def key_press(self, event):
        if event.key() != Qt.Key_Escape or self._start is None:
            return False

        self._start = None
        self._current = None
        return True

    @staticmethod
    def _is_too_short(start: QPointF, end: QPointF) -> bool:
        return hypot(end.x() - start.x(), end.y() - start.y()) <= 0.0
