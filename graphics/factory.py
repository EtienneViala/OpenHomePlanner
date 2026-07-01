"""
Graphics factory.
"""

from __future__ import annotations

from model.electrical import Outlet
from graphics.outlet_item import OutletItem


class GraphicsFactory:
    """
    Create permanent graphics items registered for project objects.

    Architectural model objects are intentionally not registered in V0.7.0:
    this version prepares data only and does not draw walls, rooms, doors or
    windows.
    """

    _registry = {}

    @staticmethod
    def register(model_type: type, item_type: type) -> None:
        """
        Register a graphics item class for a business model class.
        """
        GraphicsFactory._registry[model_type] = item_type

    @staticmethod
    def create(obj):
        item_type = GraphicsFactory._registry.get(type(obj))

        if item_type is not None:
            return item_type(obj)

        raise TypeError(
            f"No graphics item registered for {type(obj).__name__}"
        )


GraphicsFactory.register(Outlet, OutletItem)
