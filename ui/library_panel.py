from PySide6.QtWidgets import (
    QDockWidget,
    QListWidget
)


class LibraryPanel(QDockWidget):

    def __init__(self):

        super().__init__("Bibliothèque")

        self.list = QListWidget()

        self.list.addItem("⚡ Prise 16A")
        self.list.addItem("⚡ Double prise")
        self.list.addItem("💡 Point lumineux")
        self.list.addItem("🎚️ Interrupteur")
        self.list.addItem("🌐 RJ45")
        self.list.addItem("📺 TV")

        self.setWidget(self.list)