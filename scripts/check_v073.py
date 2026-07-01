#!/usr/bin/env python3
"""
Automatic validation script for OpenHomePlanner V0.7.3.

Usage:
    py scripts/check_v073.py [rochette.dxf]
"""

from __future__ import annotations

import argparse
import compileall
import os
import subprocess
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


def check_compilation() -> str:
    targets = [
        "analysis",
        "core",
        "graphics",
        "importer",
        "model",
        "tools",
        "ui",
        "main.py",
        "scripts",
        "tests",
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


def check_dxf_import(dxf_path: Path):
    from importer.dxf_importer import DXFImporter

    document = DXFImporter().load(str(dxf_path))

    if not document.entities:
        raise RuntimeError("DXF import produced no entity")

    return document, f"{len(document.entities)} entities"


def check_v072_analysis(dxf_path: Path) -> str:
    from analysis.analyzer import AnalysisReport, BuildingAnalyzer

    report = BuildingAnalyzer().analyze(dxf_path)

    if not isinstance(report, AnalysisReport):
        raise RuntimeError("analyzer did not return AnalysisReport")

    if report.dimension_count <= 0:
        raise RuntimeError("V0.7.2 analysis found no dimension candidate")

    if report.scale_factor is None:
        raise RuntimeError("V0.7.2 analysis found no calibration scale")

    return (
        f"dimensions={report.dimension_count}, "
        f"scale={report.scale_factor:.4f} {report.real_unit}/dxf"
    )


def check_wall_detector(document) -> str:
    from analysis.analyzer import BuildingAnalyzer
    from core.project import Project

    report = BuildingAnalyzer().analyze(document)

    if report.segments_analyzed <= 0:
        raise RuntimeError("WallDetector analyzed no segment")

    if report.wall_count != len(report.detected_walls):
        raise RuntimeError("wall count does not match detected wall list")

    project = Project()
    project.set_dxf_document(document)
    project.set_analysis_report(report)

    for wall in report.detected_walls:
        project.add_object(wall)

    if len(project.objects) != report.wall_count:
        raise RuntimeError("detected walls were not added through Project")

    return (
        f"{report.wall_count} wall(s), "
        f"{report.segments_analyzed} segment(s), "
        f"{report.segments_ignored} ignored, "
        f"confidence={report.confidence:.2f}"
    )


def check_non_regression(script: str, *args: str) -> str:
    env = os.environ.copy()
    env.setdefault("QT_QPA_PLATFORM", "offscreen")

    completed = subprocess.run(
        [sys.executable, str(ROOT / script), *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"{script} failed with code {completed.returncode}\n"
            f"{completed.stdout}\n{completed.stderr}"
        )

    return f"{script} returned 0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate OpenHomePlanner V0.7.3.",
    )
    parser.add_argument(
        "dxf",
        type=Path,
        nargs="?",
        default=Path("rochette.dxf"),
        help="DXF file to analyze, default: rochette.dxf",
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
    }

    runner.run("Compilation Python", check_compilation)

    def import_step() -> str:
        document, details = check_dxf_import(dxf_path)
        context["document"] = document
        return details

    runner.run("Import DXF", import_step)
    runner.run("Analyse V0.7.2", lambda: check_v072_analysis(dxf_path))

    def wall_step() -> str:
        document = context["document"]

        if document is None:
            raise RuntimeError("DXF import did not produce a document")

        return check_wall_detector(document)

    runner.run("WallDetector V0.7.3", wall_step)
    runner.run(
        "Non-regression V0.7.2",
        lambda: check_non_regression(
            "scripts/check_v072.py",
            str(dxf_path),
        ),
    )
    runner.run(
        "Non-regression V0.7.1",
        lambda: check_non_regression("scripts/check_v071.py"),
    )
    runner.run(
        "Non-regression V0.6.2",
        lambda: check_non_regression(
            "scripts/check_v062.py",
            str(dxf_path),
        ),
    )

    runner.print_summary()

    return runner.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
