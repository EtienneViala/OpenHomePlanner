from PySide6.QtWidgets import QLabel


class MousePositionLabel(QLabel):

    def set_position(self, x, y):

        self.setText(f"X : {x:.1f}    Y : {y:.1f}")