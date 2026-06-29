"""
Base graphics item.
"""

from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsItem

from model.base_object import BaseObject


class BaseItem(QGraphicsItem):

    SIZE = 20

    def __init__(self, obj: BaseObject):

        super().__init__()

        self.object = obj

        self.setPos(obj.x, obj.y)

        self.setFlags(

            QGraphicsItem.ItemIsMovable |

            QGraphicsItem.ItemIsSelectable

        )

    # ---------------------------------------------------------

    def boundingRect(self):

        s = self.SIZE

        return QRectF(

            -s / 2,

            -s / 2,

            s,

            s

        )

    # ---------------------------------------------------------

    def paint(self, painter, option, widget):

        pen = QPen(QColor("white"))

        if self.isSelected():

            pen.setColor(QColor("yellow"))

            pen.setWidth(3)

        painter.setPen(pen)

        painter.setBrush(QBrush(QColor(80, 80, 80)))

        painter.drawRect(self.boundingRect())

    # ---------------------------------------------------------

    def itemChange(self, change, value):

        if change == QGraphicsItem.ItemPositionHasChanged:

            self.object.x = self.pos().x()

            self.object.y = self.pos().y()

        return super().itemChange(change, value)