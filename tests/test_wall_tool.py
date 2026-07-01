"""
Tests for the V0.7.1 manual wall tool.
"""

from __future__ import annotations

import os
import unittest

from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QApplication

from core.project import Project
from graphics.factory import GraphicsFactory
from graphics.wall_item import WallItem
from model.architecture import DEFAULT_WALL_THICKNESS, Wall
from tools.wall_tool import WallTool
from ui.canvas import Canvas


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


class FakeMouseEvent:
    """
    Minimal mouse event accepted by Canvas and tools.
    """

    def __init__(self, x: float, y: float, button=Qt.LeftButton):
        self._position = QPointF(x, y)
        self._button = button

    def button(self):
        return self._button

    def position(self):
        return self._position


class WallToolTest(unittest.TestCase):
    """
    Validate manual wall creation and graphics integration.
    """

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.project = Project()
        self.canvas = Canvas(self.project)
        self.tool = WallTool(self.canvas)
        self.canvas.tool_manager.set_tool(self.tool)

    def tearDown(self):
        self.canvas.close()

    def test_create_wall_model(self):
        wall = Wall(
            start=(0.0, 0.0),
            end=(300.0, 400.0),
            thickness=DEFAULT_WALL_THICKNESS,
        )

        self.assertEqual(wall.length, 500.0)
        self.assertAlmostEqual(wall.angle, 53.130102, places=5)
        self.assertEqual(wall.thickness, 20.0)

    def test_add_wall_to_project_and_house(self):
        wall = Wall(start=(0.0, 0.0), end=(100.0, 0.0))

        self.project.add_object(wall)

        self.assertIn(wall, list(self.project.objects))
        self.assertEqual(self.project.house.floors[0].walls, [wall])

    def test_graphics_factory_creates_wall_item(self):
        wall = Wall(start=(0.0, 0.0), end=(100.0, 0.0))

        item = GraphicsFactory.create(wall)

        self.assertIsInstance(item, WallItem)

    def test_wall_tool_two_click_creation(self):
        self.canvas.tool_manager.mouse_press(FakeMouseEvent(0.0, 0.0))
        self.canvas.tool_manager.mouse_move(FakeMouseEvent(100.0, 0.0))

        self.assertEqual(len(self.project.objects), 0)
        self.assertIsNotNone(self.canvas._preview_item)

        self.canvas.tool_manager.mouse_press(FakeMouseEvent(100.0, 0.0))

        objects = list(self.project.objects)
        self.assertEqual(len(objects), 1)
        self.assertIsInstance(objects[0], Wall)
        self.assertEqual(objects[0].start, (0.0, 0.0))
        self.assertEqual(objects[0].end, (100.0, 0.0))
        self.assertIsNone(self.canvas._preview_item)

    def test_wall_preview_uses_existing_preview_manager(self):
        self.canvas.tool_manager.mouse_press(FakeMouseEvent(0.0, 0.0))
        self.canvas.tool_manager.mouse_move(FakeMouseEvent(100.0, 50.0))

        preview = self.canvas.tool_manager.preview

        self.assertEqual(preview._definition.shape, "wall")
        self.assertEqual(preview._definition.thickness, 20.0)
        self.assertGreater(preview._definition.length, 0.0)
        self.assertEqual(len(self.project.objects), 0)

    def test_remove_wall_from_project(self):
        wall = Wall(start=(0.0, 0.0), end=(100.0, 0.0))
        self.project.add_object(wall)

        self.project.remove_object(wall)

        self.assertNotIn(wall, list(self.project.objects))
        self.assertEqual(self.project.house.floors[0].walls, [])


if __name__ == "__main__":
    unittest.main()
