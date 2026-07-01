"""
Object manager.
"""

from model.base_object import BaseObject


class ObjectManager:

    def __init__(self):

        self._objects = []

        self._added_callbacks = []

        self._removed_callbacks = []

    @property
    def objects(self):

        return self._objects

    def add(self, obj: BaseObject):

        self._objects.append(obj)

        for callback in self._added_callbacks:
            callback(obj)

    def remove(self, obj: BaseObject):

        if obj not in self._objects:
            return

        self._objects.remove(obj)

        for callback in self._removed_callbacks:
            callback(obj)

    def clear(self):

        self._objects.clear()

    def connect(self, callback):

        self._added_callbacks.append(callback)

    def connect_removed(self, callback):

        self._removed_callbacks.append(callback)

    def __iter__(self):

        return iter(self._objects)

    def __len__(self):

        return len(self._objects)
