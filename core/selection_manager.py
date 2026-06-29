"""
Selection manager.
"""

from __future__ import annotations


class SelectionManager:

    def __init__(self):

        self._selected = None

        self._callbacks = []

    # ---------------------------------------------------------

    @property
    def current(self):

        return self._selected

    # ---------------------------------------------------------

    def set(self, obj):

        self._selected = obj

        for callback in self._callbacks:

            callback(obj)

    # ---------------------------------------------------------

    def clear(self):

        self.set(None)

    # ---------------------------------------------------------

    def connect(self, callback):

        self._callbacks.append(callback)