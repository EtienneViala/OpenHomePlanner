from dataclasses import dataclass, field


@dataclass
class Project:

    name: str = "Nouveau projet"

    layers: list = field(default_factory=list)

    objects: list = field(default_factory=list)