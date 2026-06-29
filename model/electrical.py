"""
Electrical objects
"""

from __future__ import annotations

from dataclasses import dataclass

from model.base_object import BaseObject


# ==========================================================
# Base Electrical Object
# ==========================================================

@dataclass
class ElectricalObject(BaseObject):
    """
    Base class for every electrical object.
    """

    circuit: str = ""

    height: float = 30.0

    phase: str = ""

    comment: str = ""


# ==========================================================
# Outlet
# ==========================================================

@dataclass
class Outlet(ElectricalObject):

    amperage: int = 16

    sockets: int = 1

    grounded: bool = True


# ==========================================================
# Switch
# ==========================================================

@dataclass
class Switch(ElectricalObject):

    type: str = "simple"

    controlled_light: str = ""


# ==========================================================
# Light
# ==========================================================

@dataclass
class Light(ElectricalObject):

    power: float = 10

    ceiling: bool = True


# ==========================================================
# RJ45
# ==========================================================

@dataclass
class RJ45(ElectricalObject):

    category: str = "CAT6"


# ==========================================================
# TV
# ==========================================================

@dataclass
class TV(ElectricalObject):

    satellite: bool = False