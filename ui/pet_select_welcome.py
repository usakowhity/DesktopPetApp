# ui/pet_select_welcome.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QGridLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal
from pathlib import Path

from ui.click_label import ClickLabel


class PetSelectWelcome(QWidget):
    pet_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Pet App - Welcome")
        self.setFixedSize(850, 600)

        layout = QVBoxLayout(self)

        title = QLabel("ペットを選んでね！")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        grid = QGridLayout()
        layout.addLayout(grid)

        pets = [
            ("john", "ジョン"),
            ("kuro", "くろ"),
            ("marple", "マーブル"),
            ("mary", "まり"),
            ("shiro", "しろ"),
            ("tama", "たま"),
            ("taro", "たろう"),
            ("usako", "うさこ"),
        ]

        row, col = 0, 0
        for pet_id, pet_name in pets:
            thumb_path = Path(f"assets/{pet_id}/thumb.png")

            vbox = QVBoxLayout()
            vbox.setAlignment(Qt.AlignCenter)

            label = ClickLabel()
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border: 2px solid #ccc; border-radius: 8px; padding: 4px;")

            if thumb_path.exists():
                pix = QPixmap(str(thumb_path)).scaled(
                    150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                label.setPixmap(pix)
            else:
                label.setText(pet_name)

            # ★★★ ここが最重要：引数を受け取らない lambda
            label.clicked.connect(lambda p=pet_id: self.pet_selected.emit(p))

            name_label = QLabel(pet_name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setStyleSheet("font-size: 14px; margin-top: 4px;")

            vbox.addWidget(label)
            vbox.addWidget(name_label)

            grid.addLayout(vbox, row, col)

            col += 1
            if col >= 4:
                col = 0
                row += 1

        footer = QLabel("© 2026 Pet App")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #888; margin-top: 20px;")
        layout.addWidget(footer)
