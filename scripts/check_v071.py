#!/usr/bin/env python3
"""
Automatic validation script for OpenHomePlanner V0.7.1.

Usage:
    py scripts/check_v071.py
"""

from __future__ import annotations

import compileall
import os
import sys
import traceback
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class CheckRunner:
    """
    Run validation steps and print a compact OK/FAIL summary.
    """

    def __init__(self):
        self.results: list[tuple[str, bool, str]] = []

    def run(self, name: str, callback: Callable[[], str]) -> None:
        try:
            details = callback()
        except Exception as exc:  # noqa: BLE001
            details = f"{exc}\n{traceback.format_exc(limit=2)}"
            self.results.append((name, False, details.strip()))
            print(f"[FAIL] {name} - {exc}")
            return

        self.results.append((name, True, details))
        print(f"[OK]   {name} - {details}")

    def exit_code(self) -> int:
        return 0 if all(ok for _, ok, _ in self.results) else 1

    def print_summary(self) -> None:
        print("\nSummary")
        print("-------")

        for name, ok, details in self.results:
            status = "OK" if ok else "FAIL"
            print(f"{status:4} {name}: {details}")


class FakeMouseEvent:
    """
    Minimal mouse event accepted by Canvas and tools.
    """

    def __init__(self, x: float, y: float, button):
        from PySide6.QtCore import QPointF

        self._position = QPointF(x, y)
        self._button = button

    def button(self):
        return self._button

    def position(self):
        return self._position


def check_compilation() -> str:
    targets = [
        "core",
        "graphics",
        "importer",
        "model",
        "tools",
        "ui",
        "main.py",
    ]
    failed: list[str] = []

    for target in targets:
        path = ROOT / target

        if path.is_file():
            ok = compileall.compile_file(str(path), quiet=1)
        else:
            ok = compileall.compile_dir(str(path), quiet=1)

        if not ok:
            failed.append(target)

    if failed:
        raise RuntimeError("compile failed: " + ", ".join(failed))

    return "Python sources compile"


def check_wall_model_and_factory() -> str:
    from graphics.factory import GraphicsFactory
    from graphics.wall_item import WallItem
    from model.architecture import Wall

    wall = Wall(start=(0.0, 0.0), end=(200.0, 0.0))
    item = GraphicsFactory.create(wall)

    if not isinstance(item, WallItem):
        raise RuntimeError("GraphicsFactory did not create WallItem")

    if wall.length != 200.0:
        raise RuntimeError("wall length is invalid")

    return "Wall model and WallItem registered"


def check_wall_tool_cycle() -> str:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    from core.project import Project
    from model.architecture import Wall
    from tools.wall_tool import WallTool
    from ui.canvas import Canvas

    app = QApplication.instance() or QApplication([])
    project = Project()
    canvas = Canvas(project)
    canvas.set_snap_enabled(False)
    canvas.tool_manager.set_tool(WallTool(canvas))

    before = len(project.objects)

    canvas.tool_manager.mouse_press(FakeMouseEvent(0.0, 0.0, Qt.LeftButton))
    canvas.tool_manager.mouse_move(FakeMouseEvent(200.0, 0.0, Qt.LeftButton))

    if len(project.objects) != before:
        raise RuntimeError("preview created a business object")

    if canvas._preview_item is None:
        raise RuntimeError("wall preview was not created")

    canvas.tool_manager.mouse_press(
        FakeMouseEvent(200.0, 0.0, Qt.LeftButton)
    )

    objects = list(project.objects)

    if len(objects) != before + 1:
        raise RuntimeError("wall was not added to project")

    wall = objects[-1]

    if not isinstance(wall, Wall):
        raise RuntimeError("created object is not a Wall")

    if wall not in project.house.floors[0].walls:
        raise RuntimeError("wall was not added to architectural floor")

    project.remove_object(wall)

    if wall in list(project.objects):
        raise RuntimeError("wall deletion failed")

    if wall in project.house.floors[0].walls:
        raise RuntimeError("wall remained in architectural floor")

    if app is not None:
        canvas.close()

    return "WallTool preview, creation, project add and deletion valid"


def main() -> int:
    runner = CheckRunner()

    runner.run("Compilation Python", check_compilation)
    runner.run("Wall model + WallItem", check_wall_model_and_factory)
    runner.run("WallTool + Preview + Suppression", check_wall_tool_cycle)

    runner.print_summary()

    return runner.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
