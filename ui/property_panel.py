from PySide6.QtWidgets import (
    QDockWidget,
    QFormLayout,
    QWidget,
    QLineEdit
)


class PropertyPanel(QDockWidget):

    def __init__(self):

        super().__init__("Propriétés")

        widget = QWidget()

        layout = QFormLayout()

        self.name = QLineEdit()
        self.layer = QLineEdit()
        self.rotation = QLineEdit()

        layout.addRow("Nom", self.name)
        layout.addRow("Calque", self.layer)
        layout.addRow("Rotation", self.rotation)

        widget.setLayout(layout)

        self.setWidget(widget)