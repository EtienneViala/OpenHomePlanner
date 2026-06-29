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