"""
Outlet graphics item.
"""

from PySide6.QtGui import QColor, QPen

from graphics.base_item import BaseItem


class OutletItem(BaseItem):

    SIZE = 24

    def paint(self, painter, option, widget):

        #
        # Contour de sélection
        #
        if self.isSelected():

            selection_pen = QPen(QColor("yellow"))
            selection_pen.setWidth(3)

            painter.setPen(selection_pen)
            painter.setBrush(QColor(70, 70, 70))

            painter.drawEllipse(self.boundingRect())

        #
        # Symbole de la prise
        #
        pen = QPen(QColor(0, 220, 255))
        pen.setWidth(2)

        painter.setPen(pen)
        painter.setBrush(QColor(30, 30, 30))

        r = self.boundingRect().adjusted(2, 2, -2, -2)

        painter.drawEllipse(r)

        painter.drawLine(
            r.center().x(),
            r.top() + 4,
            r.center().x(),
            r.bottom() - 4,
        )

        painter.drawLine(
            r.left() + 4,
            r.center().y(),
            r.right() - 4,
            r.center().y(),
        )