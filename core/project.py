"""
Project.
"""

from core.object_manager import ObjectManager
from core.selection_manager import SelectionManager


class Project:

    def __init__(self):

        self.name = "Untitled"

        self.objects = ObjectManager()

        self.selection = SelectionManager()

    # ---------------------------------------------------------

    def add_object(self, obj):

        self.objects.add(obj)

    # ---------------------------------------------------------

    def remove_object(self, obj):

        self.objects.remove(obj)