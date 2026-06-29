"""
Object manager.
"""

from model.base_object import BaseObject


class ObjectManager:

    def __init__(self):

        self._objects = []

        self._callbacks = []

    @property
    def objects(self):

        return self._objects

    def add(self, obj: BaseObject):

        self._objects.append(obj)

        for callback in self._callbacks:
            callback(obj)

    def remove(self, obj: BaseObject):

        self._objects.remove(obj)

    def clear(self):

        self._objects.clear()

    def connect(self, callback):

        self._callbacks.append(callback)

    def __iter__(self):

        return iter(self._objects)

    def __len__(self):

        return len(self._objects)