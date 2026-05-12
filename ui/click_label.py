# ui/click_label.py

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Signal


class ClickLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
