from PySide6.QtWidgets import (
    QMainWindow,
    QToolBar,
    QStatusBar
)

from ui.canvas import Canvas


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenHomePlanner")
        self.resize(1600, 900)

        self.canvas = Canvas()

        self.setCentralWidget(self.canvas)

        toolbar = QToolBar("Main")
        self.addToolBar(toolbar)

        self.setStatusBar(QStatusBar())