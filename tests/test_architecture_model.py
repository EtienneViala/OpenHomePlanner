"""
Unit tests for the V0.7.0 architectural model.
"""

from __future__ import annotations

import unittest

from core.project import Project
from model.architecture import Door, Floor, House, Room, Wall, Window


class ArchitectureModelTest(unittest.TestCase):
    """
    Validate architectural objects without Qt.
    """

    def test_create_house(self):
        house = House(
            name="Maison test",
            address="1 rue du Test",
            settings={"unit": "cm"},
        )

        self.assertEqual(house.name, "Maison test")
        self.assertEqual(house.address, "1 rue du Test")
        self.assertEqual(house.settings["unit"], "cm")
        self.assertEqual(house.floors, [])

    def test_create_floor(self):
        floor = Floor(
            name="RDC",
            level=0,
        )

        self.assertEqual(floor.name, "RDC")
        self.assertEqual(floor.level, 0)
        self.assertEqual(floor.rooms, [])
        self.assertEqual(floor.walls, [])

    def test_add_room(self):
        floor = Floor(name="RDC", level=0)
        room = Room(
            name="Salon",
            surface=24.5,
            contour=[
                (0.0, 0.0),
                (400.0, 0.0),
                (400.0, 600.0),
                (0.0, 600.0),
            ],
        )

        floor.add_room(room)

        self.assertEqual(floor.rooms, [room])
        self.assertEqual(room.surface, 24.5)

    def test_add_wall(self):
        floor = Floor(name="RDC", level=0)
        room = Room(name="Salon")
        wall = Wall(
            name="Mur nord",
            start=(0.0, 0.0),
            end=(400.0, 0.0),
            thickness=20.0,
            height=250.0,
            material="placeholder",
            orientation=0.0,
        )

        floor.add_wall(wall)
        room.add_wall(wall)

        self.assertEqual(floor.walls, [wall])
        self.assertEqual(room.wall_ids, [wall.uid])

    def test_add_door(self):
        wall = Wall(name="Mur entree")
        door = Door(
            name="Porte entree",
            position=120.0,
            width=90.0,
            height=204.0,
        )

        wall.add_opening(door)

        self.assertEqual(wall.openings, [door])
        self.assertEqual(door.wall_id, wall.uid)

    def test_add_window(self):
        wall = Wall(name="Mur facade")
        window = Window(
            name="Fenetre salon",
            position=180.0,
            width=120.0,
            height=115.0,
        )

        wall.add_opening(window)

        self.assertEqual(wall.openings, [window])
        self.assertEqual(window.wall_id, wall.uid)

    def test_house_serialization_roundtrip(self):
        house = House(name="Maison test")
        floor = Floor(name="RDC", level=0)
        room = Room(name="Salon", surface=24.5)
        wall = Wall(name="Mur nord")
        wall.add_opening(Door(name="Porte"))
        wall.add_opening(Window(name="Fenetre"))
        room.add_wall(wall)
        floor.add_room(room)
        floor.add_wall(wall)
        house.add_floor(floor)

        restored = House.from_dict(house.to_dict())

        self.assertEqual(restored.name, house.name)
        self.assertEqual(len(restored.floors), 1)
        self.assertEqual(len(restored.floors[0].rooms), 1)
        self.assertEqual(len(restored.floors[0].walls), 1)
        self.assertEqual(len(restored.floors[0].walls[0].openings), 2)
        self.assertIsInstance(restored.floors[0].walls[0].openings[0], Door)
        self.assertIsInstance(restored.floors[0].walls[0].openings[1], Window)

    def test_project_contains_architectural_model(self):
        project = Project()

        self.assertIsInstance(project.house, House)
        self.assertIsNone(project.dxf_document)


if __name__ == "__main__":
    unittest.main()
