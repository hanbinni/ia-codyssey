from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

def format_number(num_str):
    try:
        if '.' in num_str:
            integer_part, decimal_part = num_str.split('.')
            integer_part = f"{int(integer_part):,}"
            return f"{integer_part}.{decimal_part}"
        else:
            return f"{int(num_str):,}"
    except:
        return num_str

class IPhoneCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Calculator - PyQt5 Clone")
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(360, 600)

        self.expression = ""
        self.result_displayed = False
        self.init_ui()

    def init_ui(self):
        self.result = QLabel("0")
        self.result.setStyleSheet("color: white; font-size: 56px; font-weight: bold;")
        self.result.setAlignment(Qt.AlignRight)

        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["⌸", "0", ".", "="]
        ]

        grid = QGridLayout()
        grid.setSpacing(10)

        for row, row_data in enumerate(buttons):
            for col, text in enumerate(row_data):
                btn = QPushButton(text)
                btn.setFixedSize(80, 80)
                btn.setFont(QFont("Helvetica", 20))
                btn.setStyleSheet(self.get_button_style(text))
                btn.clicked.connect(lambda _, t=text: self.on_button_click(t))
                if text == "AC":
                    self.clear_btn = btn
                grid.addWidget(btn, row, col)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.result)
        layout.addSpacing(10)
        layout.addLayout(grid)
        self.setLayout(layout)

    def get_button_style(self, text):
        if text in ["÷", "×", "-", "+", "="]:
            return """
                QPushButton {
                    background-color: #FF9500;
                    color: white;
                    border-radius: 40px;
                }
                QPushButton:pressed {
                    background-color: #cc7a00;
                }
            """
        elif text in ["AC", "+/-", "%", "⌸"]:
            return """
                QPushButton {
                    background-color: #505050;
                    color: white;
                    border-radius: 40px;
                }
                QPushButton:pressed {
                    background-color: #666666;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #1C1C1C;
                    color: white;
                    border-radius: 40px;
                }
                QPushButton:pressed {
                    background-color: #333333;
                }
            """

    def update_display(self):
        display = self.expression if self.expression else "0"
        self.result.setText(display)
        self.clear_btn.setText("⌫" if self.expression else "AC")

    def on_button_click(self, key):
        if key in "0123456789":
            if self.result_displayed:
                self.expression = ""
                self.result_displayed = False
            self.expression += key
            self.update_display()

        elif key == ".":
            if self.result_displayed:
                self.expression = ""
                self.result_displayed = False
            if not self.expression or not self.expression[-1].isdigit():
                self.expression += "0."
            elif "." not in self.get_last_number():
                self.expression += "."
            self.update_display()

        elif key in ["+", "-", "×", "÷"]:
            if self.expression and self.expression[-1] not in "+-×÷":
                self.expression += key
            elif self.expression and self.expression[-1] in "+-×÷":
                self.expression = self.expression[:-1] + key
            self.update_display()

        elif key == "=":
            try:
                expr = self.expression.replace("×", "*").replace("÷", "/")
                result = str(eval(expr))
                if result.endswith(".0"):
                    result = result[:-2]
                self.result.setText(format_number(result))
                self.result_displayed = True
                self.expression = result
                self.clear_btn.setText("AC")
            except:
                self.result.setText("Error")
                self.expression = ""
                self.result_displayed = True

        elif key in ["AC", "⌫"]:
            if self.clear_btn.text() == "⌫":
                self.expression = self.expression[:-1]
            else:
                self.expression = ""
            self.result_displayed = False
            self.update_display()

        elif key == "+/-":
            try:
                last = self.get_last_number()
                if not last:
                    return
                if last.startswith("-"):
                    new = last[1:]
                else:
                    new = "-" + last
                self.expression = self.expression[:-len(last)] + new
                self.update_display()
            except:
                pass

        elif key == "%":
            try:
                last = self.get_last_number()
                if not last:
                    return
                new = str(float(last) / 100)
                if new.endswith(".0"):
                    new = new[:-2]
                self.expression = self.expression[:-len(last)] + new
                self.update_display()
            except:
                pass

    def get_last_number(self):
        tokens = []
        for ch in reversed(self.expression):
            if ch in "+-×÷":
                break
            tokens.append(ch)
        return ''.join(reversed(tokens))

if __name__ == "__main__":
    app = QApplication([])
    calc = IPhoneCalculator()
    calc.show()
    app.exec_()
