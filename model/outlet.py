from dataclasses import dataclass


@dataclass
class Outlet:

    x: float

    y: float

    rotation: float = 0

    circuit: str = ""

    layer: str = "Electrical"