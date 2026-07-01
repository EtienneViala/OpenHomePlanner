"""
Project.
"""

from __future__ import annotations

from core.object_manager import ObjectManager
from core.selection_manager import SelectionManager
from model.architecture import House


class Project:
    """
    Central project model.

    The project owns every business model: imported plan data, architectural
    model, placed objects and selection state.
    """

    def __init__(self):

        self.name = "Untitled"
        self.dxf_document = None
        self.house = House(name="Maison")

        self.objects = ObjectManager()

        self.selection = SelectionManager()

    # ---------------------------------------------------------

    def add_object(self, obj):

        self.objects.add(obj)

    # ---------------------------------------------------------

    def remove_object(self, obj):

        self.objects.remove(obj)

    # ---------------------------------------------------------

    def set_dxf_document(self, document) -> None:
        """
        Store the imported DXF document in the project.
        """
        self.dxf_document = document

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
        }
