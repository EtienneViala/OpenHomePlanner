"""
Graphics factory.
"""

from model.electrical import Outlet
from graphics.outlet_item import OutletItem


class GraphicsFactory:

    @staticmethod
    def create(obj):

        if isinstance(obj, Outlet):
            return OutletItem(obj)

        raise TypeError(
            f"No graphics item registered for {type(obj).__name__}"
        )