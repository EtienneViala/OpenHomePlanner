"""
OpenHomePlanner

Base class for every object in the project.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class BaseObject:
    """
    Base object stored in a project.

    Every element (wall, outlet, light, door, pipe...)
    inherits from this class.
    """

    # Unique identifier
    uid: str = field(default_factory=lambda: str(uuid4()))

    # Position (cm)
    x: float = 0.0
    y: float = 0.0

    # Rotation (degrees)
    rotation: float = 0.0

    # Layer name
    layer: str = "Default"

    # Display name
    name: str = ""

    # Visibility
    visible: bool = True

    # Selection
    selected: bool = False

    # Locked
    locked: bool = False

    def move(self, dx: float, dy: float) -> None:
        """
        Move the object.
        """
        self.x += dx
        self.y += dy

    def set_position(self, x: float, y: float) -> None:
        """
        Set absolute position.
        """
        self.x = x
        self.y = y

    def rotate(self, angle: float) -> None:
        """
        Rotate the object.
        """
        self.rotation = angle

    def serialize(self) -> dict:
        """
        Convert object into JSON serializable dictionary.
        """
        return {
            "uid": self.uid,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "rotation": self.rotation,
            "layer": self.layer,
            "visible": self.visible,
            "locked": self.locked,
        }