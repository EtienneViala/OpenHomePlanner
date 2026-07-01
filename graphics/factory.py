"""
Graphics factory.
"""

from __future__ import annotations

from model.electrical import Outlet
from model.architecture import Wall
from graphics.outlet_item import OutletItem
from graphics.wall_item import WallItem


class GraphicsFactory:
    """
    Create permanent graphics items registered for project objects.

    Graphics items are registered by model type so new tools can extend the
    application without adding object-specific if/else branches.
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
GraphicsFactory.register(Wall, WallItem)
