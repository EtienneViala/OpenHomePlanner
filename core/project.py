"""
Project.
"""

from __future__ import annotations

from core.object_manager import ObjectManager
from core.selection_manager import SelectionManager
from model.architecture import Floor, House, Wall


class Project:
    """
    Central project model.

    The project owns every business model: imported plan data, architectural
    model, placed objects and selection state.
    """

    def __init__(self):

        self.name = "Untitled"
        self.dxf_document = None
        self.analysis_report = None
        self.house = House(name="Maison")

        self.objects = ObjectManager()

        self.selection = SelectionManager()

    # ---------------------------------------------------------

    def add_object(self, obj):

        if isinstance(obj, Wall):
            self._default_floor().add_wall(obj)

        self.objects.add(obj)

    # ---------------------------------------------------------

    def remove_object(self, obj):

        if isinstance(obj, Wall):
            for floor in self.house.floors:
                if obj in floor.walls:
                    floor.walls.remove(obj)

        self.objects.remove(obj)

    # ---------------------------------------------------------

    def detected_walls(self) -> list[Wall]:
        """
        Return detected walls currently stored in the project.
        """
        return [
            obj
            for obj in self.objects
            if isinstance(obj, Wall)
            and getattr(obj, "source", "manual") == "detected"
        ]

    # ---------------------------------------------------------

    def remove_detected_walls(self) -> int:
        """
        Remove only automatically detected walls through the standard flow.
        """
        walls = self.detected_walls()

        for wall in walls:
            self.remove_object(wall)

        return len(walls)

    # ---------------------------------------------------------

    def set_dxf_document(self, document) -> None:
        """
        Store the imported DXF document in the project.
        """
        self.dxf_document = document

    # ---------------------------------------------------------

    def set_analysis_report(self, report) -> None:
        """
        Store the latest building analysis report.
        """
        self.analysis_report = report

    # ---------------------------------------------------------

    def _default_floor(self) -> Floor:
        """
        Return the default floor used by manual architectural tools.
        """
        if not self.house.floors:
            self.house.add_floor(
                Floor(
                    name="RDC",
                    level=0,
                )
            )

        return self.house.floors[0]

    # ---------------------------------------------------------

    def to_dict(self) -> dict:
        """
        Serialize the project data that is ready for persistence.
        """
        return {
            "name": self.name,
            "house": self.house.to_dict(),
            "object_count": len(self.objects),
            "has_dxf_document": self.dxf_document is not None,
            "analysis_report": (
                self.analysis_report.to_dict()
                if self.analysis_report is not None
                else None
            ),
        }
