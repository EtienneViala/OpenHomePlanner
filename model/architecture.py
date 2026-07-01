"""
Architectural data model for OpenHomePlanner.

The classes in this module are pure Python data objects. They do not depend on
Qt and do not draw anything. They prepare the project for future wall tools and
building analysis features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import atan2, degrees, hypot
from uuid import uuid4


Point = tuple[float, float]
DEFAULT_WALL_THICKNESS = 20.0


def _new_uid() -> str:
    return str(uuid4())


@dataclass
class ArchitecturalObject:
    """
    Base class for architectural model objects.
    """

    name: str = ""
    uid: str = field(default_factory=_new_uid)

    def base_dict(self) -> dict:
        """
        Serialize common attributes.
        """
        return {
            "type": self.__class__.__name__,
            "uid": self.uid,
            "name": self.name,
        }


@dataclass
class Opening(ArchitecturalObject):
    """
    Base class for an opening hosted by a wall.
    """

    position: float = 0.0
    width: float = 0.0
    height: float = 0.0
    wall_id: str | None = None

    def to_dict(self) -> dict:
        data = self.base_dict()
        data.update(
            {
                "position": self.position,
                "width": self.width,
                "height": self.height,
                "wall_id": self.wall_id,
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Opening:
        opening_type = data.get("type", "Opening")
        opening_class = {
            "Opening": Opening,
            "Door": Door,
            "Window": Window,
        }.get(opening_type, Opening)

        return opening_class(
            name=data.get("name", ""),
            uid=data.get("uid", _new_uid()),
            position=data.get("position", 0.0),
            width=data.get("width", 0.0),
            height=data.get("height", 0.0),
            wall_id=data.get("wall_id"),
        )


@dataclass
class Door(Opening):
    """
    Door opening.

    Specific behavior will be added in a later version.
    """


@dataclass
class Window(Opening):
    """
    Window opening.

    Specific behavior will be added in a later version.
    """


@dataclass
class Wall(ArchitecturalObject):
    """
    Wall segment stored in the architectural model.
    """

    start: Point = (0.0, 0.0)
    end: Point = (0.0, 0.0)
    thickness: float = DEFAULT_WALL_THICKNESS
    height: float = 250.0
    material: str = ""
    orientation: float = 0.0
    source: str = "manual"
    confidence: float = 1.0
    detection_id: str | None = None
    metadata: dict = field(default_factory=dict)
    openings: list[Opening] = field(default_factory=list)

    @property
    def length(self) -> float:
        """
        Return the wall length in project units.
        """
        return hypot(
            self.end[0] - self.start[0],
            self.end[1] - self.start[1],
        )

    @property
    def angle(self) -> float:
        """
        Return the wall angle in degrees.
        """
        return degrees(
            atan2(
                self.end[1] - self.start[1],
                self.end[0] - self.start[0],
            )
        )

    def move(self, dx: float, dy: float) -> None:
        """
        Move both wall endpoints.
        """
        self.start = (
            self.start[0] + dx,
            self.start[1] + dy,
        )
        self.end = (
            self.end[0] + dx,
            self.end[1] + dy,
        )

    def add_opening(self, opening: Opening) -> None:
        """
        Attach an opening to this wall.
        """
        opening.wall_id = self.uid
        self.openings.append(opening)

    def to_dict(self) -> dict:
        data = self.base_dict()
        data.update(
            {
                "start": list(self.start),
                "end": list(self.end),
                "thickness": self.thickness,
                "height": self.height,
                "material": self.material,
                "orientation": self.orientation,
                "source": self.source,
                "confidence": self.confidence,
                "detection_id": self.detection_id,
                "metadata": dict(self.metadata),
                "length": self.length,
                "angle": self.angle,
                "openings": [
                    opening.to_dict()
                    for opening in self.openings
                ],
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Wall:
        wall = cls(
            name=data.get("name", ""),
            uid=data.get("uid", _new_uid()),
            start=tuple(data.get("start", (0.0, 0.0))),
            end=tuple(data.get("end", (0.0, 0.0))),
            thickness=data.get("thickness", DEFAULT_WALL_THICKNESS),
            height=data.get("height", 250.0),
            material=data.get("material", ""),
            orientation=data.get("orientation", 0.0),
            source=data.get("source", "manual"),
            confidence=data.get("confidence", 1.0),
            detection_id=data.get("detection_id"),
            metadata=dict(data.get("metadata", {})),
        )

        for opening_data in data.get("openings", []):
            wall.openings.append(Opening.from_dict(opening_data))

        return wall


@dataclass
class Room(ArchitecturalObject):
    """
    Room stored as a named area with a future-ready contour.
    """

    surface: float = 0.0
    contour: list[Point] = field(default_factory=list)
    wall_ids: list[str] = field(default_factory=list)

    def add_wall(self, wall: Wall) -> None:
        """
        Reference a wall used by this room.
        """
        if wall.uid not in self.wall_ids:
            self.wall_ids.append(wall.uid)

    def to_dict(self) -> dict:
        data = self.base_dict()
        data.update(
            {
                "surface": self.surface,
                "contour": [
                    list(point)
                    for point in self.contour
                ],
                "wall_ids": list(self.wall_ids),
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Room:
        return cls(
            name=data.get("name", ""),
            uid=data.get("uid", _new_uid()),
            surface=data.get("surface", 0.0),
            contour=[
                tuple(point)
                for point in data.get("contour", [])
            ],
            wall_ids=list(data.get("wall_ids", [])),
        )


@dataclass
class Floor(ArchitecturalObject):
    """
    Floor containing rooms and walls.
    """

    level: int = 0
    rooms: list[Room] = field(default_factory=list)
    walls: list[Wall] = field(default_factory=list)

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def add_wall(self, wall: Wall) -> None:
        if wall not in self.walls:
            self.walls.append(wall)

    def to_dict(self) -> dict:
        data = self.base_dict()
        data.update(
            {
                "level": self.level,
                "rooms": [
                    room.to_dict()
                    for room in self.rooms
                ],
                "walls": [
                    wall.to_dict()
                    for wall in self.walls
                ],
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Floor:
        floor = cls(
            name=data.get("name", ""),
            uid=data.get("uid", _new_uid()),
            level=data.get("level", 0),
        )

        for room_data in data.get("rooms", []):
            floor.add_room(Room.from_dict(room_data))

        for wall_data in data.get("walls", []):
            floor.add_wall(Wall.from_dict(wall_data))

        return floor


@dataclass
class House(ArchitecturalObject):
    """
    Complete house model stored in a project.
    """

    address: str = ""
    floors: list[Floor] = field(default_factory=list)
    settings: dict = field(default_factory=dict)

    def add_floor(self, floor: Floor) -> None:
        self.floors.append(floor)

    def to_dict(self) -> dict:
        data = self.base_dict()
        data.update(
            {
                "address": self.address,
                "floors": [
                    floor.to_dict()
                    for floor in self.floors
                ],
                "settings": dict(self.settings),
            }
        )
        return data

    @classmethod
    def from_dict(cls, data: dict) -> House:
        house = cls(
            name=data.get("name", ""),
            uid=data.get("uid", _new_uid()),
            address=data.get("address", ""),
            settings=dict(data.get("settings", {})),
        )

        for floor_data in data.get("floors", []):
            house.add_floor(Floor.from_dict(floor_data))

        return house
