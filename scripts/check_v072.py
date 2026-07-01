#!/usr/bin/env python3
"""
Automatic validation script for OpenHomePlanner V0.7.2.

Usage:
    py scripts/check_v072.py [rochette.dxf]
"""

from __future__ import annotations

import argparse
import compileall
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


def check_unit_detection(dxf_path: Path) -> str:
    from analysis.detectors.unit_detector import UnitDetector

    result = UnitDetector().detect(dxf_path)

    if not result.unit:
        raise RuntimeError("unit detector returned no unit")

    return f"unit={result.unit}, confidence={result.confidence:.2f}"


def check_dimension_detection(dxf_path: Path) -> str:
    from analysis.detectors.dimension_detector import DimensionDetector

    result = DimensionDetector().detect(dxf_path)

    if result.dimensions is None:
        raise RuntimeError("dimension detector returned no list")

    return f"{len(result.dimensions)} dimension candidate(s)"


def check_analysis_report(dxf_path: Path) -> str:
    from analysis.analyzer import AnalysisReport, BuildingAnalyzer
    from core.project import Project

    report = BuildingAnalyzer().analyze(dxf_path)

    if not isinstance(report, AnalysisReport):
        raise RuntimeError("analyzer did not return AnalysisReport")

    data = report.to_dict()
    restored = AnalysisReport.from_dict(data)

    if restored.to_dict() != data:
        raise RuntimeError("AnalysisReport serialization roundtrip failed")

    project = Project()
    project.set_analysis_report(report)

    if project.to_dict()["analysis_report"] != data:
        raise RuntimeError("Project did not serialize latest report")

    return (
        f"report unit={report.detected_unit}, "
        f"dimensions={report.dimension_count}, "
        f"scale={report.scale_factor} {report.real_unit}/dxf, "
        f"confidence={report.confidence:.2f}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate OpenHomePlanner V0.7.2.",
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
    runner.run("Lecture des unites", lambda: check_unit_detection(dxf_path))
    runner.run(
        "Detection des cotations",
        lambda: check_dimension_detection(dxf_path),
    )
    runner.run(
        "Rapport et serialisation",
        lambda: check_analysis_report(dxf_path),
    )

    runner.print_summary()

    return runner.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
