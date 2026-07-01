#!/usr/bin/env python3
"""
Automatic validation script for OpenHomePlanner V0.6.2.

Usage:
    py scripts/check_v062.py rochette.dxf
"""

from __future__ import annotations

import argparse
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
        except Exception as exc:  # noqa: BLE001 - check script reports all failures
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


def check_compilation() -> str:
    targets = [
        "core",
        "graphics",
        "importer",
        "model",
        "tools",
        "ui",
        "main.py",
        "test_dfx.py",
    ]

    failed: list[str] = []

    for target in targets:
        path = ROOT / target

        if not path.exists():
            failed.append(f"{target} missing")
            continue

        if path.is_dir():
            ok = compileall.compile_dir(
                str(path),
                quiet=1,
            )
        else:
            ok = compileall.compile_file(
                str(path),
                quiet=1,
            )

        if not ok:
            failed.append(target)

    if failed:
        raise RuntimeError("compile failed: " + ", ".join(failed))

    return "Python sources compile"


def check_dxf_import(dxf_path: Path):
    from importer.dxf_importer import DXFImporter

    document = DXFImporter().load(str(dxf_path))
    count = len(document.entities)

    if count <= 0:
        raise RuntimeError("DXF contains no imported entity")

    if dxf_path.name.lower() == "rochette.dxf" and count != 191:
        raise RuntimeError(
            f"rochette.dxf should contain 191 entities, got {count}"
        )

    return document, f"{count} entities"


def check_dxf_layers(document) -> str:
    layer_names = sorted(document.layers)

    if not layer_names:
        raise RuntimeError("no DXF layer found")

    return ", ".join(layer_names)


def check_qt_smoke():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    from PySide6.QtWidgets import QApplication

    from ui.main_window import MainWindow

    app = QApplication.instance()
    owns_app = app is None

    if app is None:
        app = QApplication([])

    window = MainWindow()

    required_attrs = {
        "canvas": hasattr(window, "canvas"),
        "toolbar": hasattr(window, "toolbar"),
        "statusbar": window.statusBar() is not None,
        "layers panel": hasattr(window, "layers"),
        "library panel": hasattr(window, "library"),
        "property panel": hasattr(window, "properties"),
    }

    missing = [
        name
        for name, present in required_attrs.items()
        if not present
    ]

    if missing:
        raise RuntimeError("missing UI component(s): " + ", ".join(missing))

    return app, window, owns_app, "MainWindow components available"


def check_outlet_tool(window) -> str:
    from graphics.factory import GraphicsFactory
    from model.electrical import Outlet

    window.activate_tool("outlet")

    project = window.project
    before = len(project.objects)

    outlet = Outlet(
        x=100.0,
        y=150.0,
        name="Check V0.6.2",
    )
    project.add_object(outlet)

    after = len(project.objects)

    if after != before + 1:
        raise RuntimeError("project object count did not increase")

    item = GraphicsFactory.create(outlet)

    if item is None:
        raise RuntimeError("GraphicsFactory returned no item")

    return f"Outlet added and graphics item created ({before} -> {after})"


def check_remove_object(window) -> str:
    objects = list(window.project.objects)

    if not objects:
        raise RuntimeError("no object available for removal")

    obj = objects[-1]
    before = len(window.project.objects)
    window.project.remove_object(obj)
    after = len(window.project.objects)

    if obj in list(window.project.objects):
        raise RuntimeError("removed object is still in project")

    if after != before - 1:
        raise RuntimeError("project object count did not decrease")

    return f"Object removed ({before} -> {after})"


def check_ghost_preview(window) -> str:
    from PySide6.QtCore import QPointF

    from core.preview import PreviewDefinition
    from graphics.preview_manager import PreviewManager

    canvas = window.canvas

    if not hasattr(canvas.tool_manager, "preview"):
        raise RuntimeError("ToolManager has no preview manager")

    if not isinstance(canvas.tool_manager.preview, PreviewManager):
        raise RuntimeError("unexpected preview manager type")

    before = len(window.project.objects)

    preview = canvas.tool_manager.preview
    preview.set_preview(
        PreviewDefinition(shape="circle_cross", size=24.0)
    )
    preview.move_to(QPointF(10.0, 20.0))

    if canvas._preview_item is None:
        raise RuntimeError("preview item was not created")

    preview.move_to(QPointF(30.0, 40.0))

    if canvas._preview_item.pos() != QPointF(30.0, 40.0):
        raise RuntimeError("preview item did not move")

    preview.clear()

    if canvas._preview_item is not None:
        raise RuntimeError("preview item was not removed")

    after = len(window.project.objects)

    if after != before:
        raise RuntimeError("preview created a business object")

    return "Preview created, moved and removed without project mutation"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate OpenHomePlanner V0.6.2.",
    )
    parser.add_argument(
        "dxf",
        type=Path,
        help="DXF file to import, for example rochette.dxf",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dxf_path = args.dxf

    if not dxf_path.is_absolute():
        dxf_path = ROOT / dxf_path

    runner = CheckRunner()
    context = {
        "document": None,
        "app": None,
        "window": None,
        "owns_app": False,
    }

    runner.run("Compilation Python", check_compilation)

    def import_step() -> str:
        document, details = check_dxf_import(dxf_path)
        context["document"] = document
        return details

    runner.run("Import DXF", import_step)

    def layers_step() -> str:
        document = context["document"]
        if document is None:
            raise RuntimeError("DXF import did not produce a document")
        return check_dxf_layers(document)

    runner.run("Calques DXF", layers_step)

    def qt_step() -> str:
        app, window, owns_app, details = check_qt_smoke()
        context["app"] = app
        context["window"] = window
        context["owns_app"] = owns_app
        return details

    runner.run("Smoke test Qt", qt_step)

    def outlet_step() -> str:
        window = context["window"]
        if window is None:
            raise RuntimeError("Qt smoke test did not create MainWindow")
        return check_outlet_tool(window)

    runner.run("Test outil Prise", outlet_step)

    def remove_step() -> str:
        window = context["window"]
        if window is None:
            raise RuntimeError("Qt smoke test did not create MainWindow")
        return check_remove_object(window)

    runner.run("Test suppression", remove_step)

    def preview_step() -> str:
        window = context["window"]
        if window is None:
            raise RuntimeError("Qt smoke test did not create MainWindow")
        return check_ghost_preview(window)

    runner.run("Ghost Preview", preview_step)

    window = context["window"]
    if window is not None:
        window.close()

    app = context["app"]
    if app is not None and context["owns_app"]:
        app.quit()

    runner.print_summary()

    return runner.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
