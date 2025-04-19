import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt


class IOSStyleCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iOS 스타일 계산기")
        self.setFixedSize(360, 600)
        self.setStyleSheet("background-color: black;")
        self.init_ui()

    def init_ui(self):
        # 디스플레이 라벨
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                padding: 20px;
            }
        """)
        self.display.setFixedHeight(100)

        # 버튼 레이아웃 구성
        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="],
        ]

        grid = QGridLayout()
        grid.setSpacing(10)

        for row_idx, row in enumerate(buttons):
            col_offset = 0
            for col_idx, btn_text in enumerate(row):
                # "0" 버튼은 두 칸 차지
                if btn_text == "0":
                    btn = self.create_button(btn_text, width=170)
                    grid.addWidget(btn, row_idx, 0, 1, 2)
                    col_offset = 1  # 다음 버튼 위치 보정
                    continue

                col = col_idx + col_offset
                btn = self.create_button(btn_text)
                grid.addWidget(btn, row_idx, col)

        # 전체 레이아웃
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.display)
        main_layout.addLayout(grid)
        main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(main_layout)

    def create_button(self, text, width=80, height=80):
        # 색상 설정
        if text in ["÷", "×", "-", "+", "="]:
            bg_color = "#FF9500"  # 오렌지
            fg_color = "white"
        elif text in ["AC", "+/-", "%"]:
            bg_color = "#D4D4D2"  # 연회색
            fg_color = "black"
        else:
            bg_color = "#505050"  # 어두운 회색
            fg_color = "white"

        button = QPushButton(text)
        button.setFixedSize(width, height)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {fg_color};
                border: none;
                border-radius: {height//2}px;
                font-size: 26px;
            }}
            QPushButton:pressed {{
                background-color: #888888;
            }}
        """)
        return button


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = IOSStyleCalculator()
    win.show()
    sys.exit(app.exec_())
