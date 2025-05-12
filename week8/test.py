from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from styles import get_button_style  # 외부 스타일 함수 사용

# 자릿수에 따른 버튼 크기 조정 (앱 크기를 고정해놨기에 하드코딩으로 수행 플렉서블할 필요가 없음)
def adjust_font_size(text):
    length = len(text)
    if length <= 10:
        font_size = 56
    elif length <= 13:
        font_size = 48
    elif length <= 15:
        font_size = 40
    elif length <= 20:
        font_size = 32
    else:
        font_size = 24 
    return font_size 

# 입력값을 분할하는 메서드
def split_expression(expr):
    tokens = []
    number = ""
    i = 0

    while i < len(expr):
        char = expr[i]

        # 숫자나 '.'은 계속 누적
        if char.isdigit() or char == '.':
            number += char

        # 부호 '-' 처리
        elif char == "-":
            # '-'가 맨 앞이거나 연산자 뒤일 경우, 음수 시작
            if i == 0 or expr[i - 1] in "+-×÷":
                number += char  # 음수 부호로 누적
            else:
                if number:
                    tokens.append(number)
                    number = ""
                tokens.append("-")

        # 연산자 처리
        elif char in "+×÷":
            if number:
                tokens.append(number)
                number = ""
            tokens.append(char)

        # % 처리
        elif char == "%" and number:
            tokens.append(number)
            tokens.append("%")
            number = ""

        i += 1

    if number:
        tokens.append(number)

    return tokens

# 1000자리 "," 처리
def format_number_with_commas(expr):
    tokens = []
    number = ""
    for char in expr:
        if char in "+-×÷":
            if number:
                tokens.append(number)
                number = ""
            tokens.append(char)
        else:
            number += char
    if number:
        tokens.append(number)

    formatted = []
    for token in tokens:
        if token not in "+-×÷":
            try:
                if token.endswith('%'):
                    value = token[:-1]
                    if "." in value:
                        integer_part, decimal_part = value.split(".")
                        integer_part = f"{int(integer_part):,}"
                        formatted.append(f"{integer_part}.{decimal_part}%")
                    else:
                        formatted.append(f"{int(value):,}%")
                elif "." in token:
                    integer_part, decimal_part = token.split(".")
                    integer_part = f"{int(integer_part):,}"
                    formatted.append(f"{integer_part}.{decimal_part}")
                else:
                    formatted.append(f"{int(token):,}")
            except:
                formatted.append(token)
        else:
            formatted.append(token)
    return "".join(formatted)

# 마지막 숫자 대체하기 (부호전환 ,퍼센트, 소수점 를 위해)
def replace_last_number(display_expression, new_val):
    last_number = get_last_number(display_expression)
    i = len(display_expression) - len(last_number)
    return display_expression[:i] + new_val

# 마지막 숫자 가져오기 (부호전환 및 퍼센트 처리를 위해)
def get_last_number(expr):
    num = ""
    i = len(expr) - 1
    paren_count = 0
    while i >= 0:
        c = expr[i]
        if c == ")":
            paren_count += 1
            num = c + num
        elif c == "(":
            paren_count -= 1
            num = c + num
            if paren_count <= 0:
                break
        elif c in "+-×÷" and paren_count == 0:
            break
        else:
            num = c + num
        i -= 1
    return num

# 음수의 괄호 계산 처리
def preprocess_expression(expr):
    new_expr = ""
    i = 0
    print("원래 수식:", expr)

    while i < len(expr):
        if expr[i:i+2] == "(-":
            i += 2
            num = ""
            while i < len(expr) and (expr[i].isdigit() or expr[i] == "." or expr[i] == "%"):
                num += expr[i]
                i += 1

            if i < len(expr) and expr[i] == ")":
                new_expr += "-" + num
                i += 1
            else:
                new_expr += "(-" + num
        else:
            new_expr += expr[i]
            i += 1

    return new_expr



class Calculator(QWidget):
    def __init__(self): # 초기화
        super().__init__()
        self.setWindowTitle("iPhone Calculator - PyQt5 Clone")
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(360, 600)
        
        self.current_input = ""
        self.display_expression = ""
        self.result_displayed = False

        self.init_ui()

    def init_ui(self): # UI 초기화
        self.formula = QLabel("")
        self.formula.setStyleSheet("color: #A5A5A5; font-size: 20px;")
        self.formula.setAlignment(Qt.AlignRight)

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
        
        #버튼 처리
        for row, row_data in enumerate(buttons):
            for col, text in enumerate(row_data):
                btn = QPushButton(text)
                btn.setFixedSize(80, 80)
                btn.setFont(QFont("Helvetica", 20))
                btn.setStyleSheet(get_button_style(text))
                btn.clicked.connect(lambda _, t=text: self.on_button_click(t))
                if text == "AC":
                    self.clear_btn = btn
                grid.addWidget(btn, row, col)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.formula)
        layout.addWidget(self.result)
        layout.addSpacing(10)
        layout.addLayout(grid)

        self.setLayout(layout)
        
    # 화면 업데이트
    def update_display(self):
        if self.result_displayed:
            self.result.setText(format_number_with_commas(self.current_input))
            self.clear_btn.setText("AC")
        else:
            self.result.setText(format_number_with_commas(self.display_expression or "0"))
            self.clear_btn.setText("⌫" if self.display_expression else "AC")

        font_size = adjust_font_size(self.result.text())
    
        # 폰트 크기 스타일 적용
        self.result.setStyleSheet(f"color: white; font-size: {font_size}px; font-weight: bold;")      
         
    # 버튼 클릭 이벤트 처리
    def on_button_click(self, key):
        if key in "0123456789":
            if self.result_displayed:
                self.display_expression = ""
                self.result_displayed = False
            self.display_expression += key
            self.update_display()

        elif key == ".":
            if self.result_displayed:
                self.display_expression = "0"
                self.result_displayed = False
            if not self.display_expression or self.display_expression[-1] in "+-×÷":
                self.display_expression += "0."
            else:
                last = get_last_number(self.display_expression)
                if "." not in last:
                    self.display_expression += "."
            self.update_display()

        elif key in ["+", "-", "×", "÷"]:
            if self.result_displayed:
                self.display_expression = self.current_input
                self.result_displayed = False
            if not self.display_expression:
                self.display_expression = "0"
            if self.display_expression[-1:] in "+-×÷":
                self.display_expression = self.display_expression[:-1] + key
            else:
                self.display_expression += key
            self.update_display()

        elif key == "=":
            self.equal()

        elif key in ["AC", "⌫"]:
            if self.clear_btn.text() == "⌫" and self.display_expression:
                self.display_expression = self.display_expression[:-1]
                self.update_display()
            else:
                self.reset()

        elif key == "+/-":
            self.negative_positive()

        elif key == "%":
            self.percent()
        
        elif key == "⌸":
            pass  # 아이폰 계산기에 있길래 그냥 넣어봤습니다.

    # 이하 연산 메서드드
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다.")
        return a / b

    # ac 버튼 처리
    def reset(self):
        self.display_expression = ""
        self.current_input = ""
        self.result_displayed = False
        self.formula.setText("")
        self.result.setText("0")
        self.clear_btn.setText("AC")

    # 부호전환 처리
    def negative_positive(self):
        num = get_last_number(self.display_expression)
        if num:
            if num.startswith("(-") and num.endswith(")"):
                num = num[2:-1]
            else:
                num = f"(-{num})"
            self.display_expression = replace_last_number(self.display_expression, num)
            self.update_display()
    
    # 백분율 처리      
    def percent(self):
        num = get_last_number(self.display_expression)
        if num and not num.endswith('%'):
            self.display_expression = replace_last_number(self.display_expression, num + "%")
            self.update_display()
            
    # "=" 결과 출력 메서드
    def equal(self):
        # 수식이 연산자(+, -, ×, ÷)로 끝나는지 체크
        if self.display_expression and self.display_expression[-1] in "+-×÷":
            return  # 계산할 수 없으므로 아무 작업도 하지 않음
        
        # 수식이 숫자 뒤에 .이만 남아있는지 체크 (예: 99. or 99.9)
        if self.display_expression and self.display_expression[-1] == ".":
            return  # 계산할 수 없으므로 아무 작업도 하지 않음

        # 부호로 시작하는 수식을 처리 (예: -9, +9와 같은 수는 계산 가능)
        if self.display_expression and self.display_expression[0] == "-" and len(self.display_expression) == 1:
            return  # -9와 같은 수는 계산할 수 없으므로 return
        
        result = self.evaluate_expression()
        if result == "DIV_ZERO":
            self.formula.setText(format_number_with_commas(self.display_expression))
            self.result.setText("정의되지 않음")
            self.display_expression = ""
            self.result_displayed = True
        elif result == "SYNTAX_ERROR":
            self.result.setText("잘못된 수식")
            self.formula.setText("")
            self.display_expression = ""
            self.result_displayed = True
        elif result == "OVERFLOW_ERROR":
            self.result.setText("범위를 초과한 수")
            self.formula.setText("")
            self.display_expression = ""
            self.result_displayed = True
        elif result == "Error":
            self.result.setText("오류")
            self.formula.setText("")
            self.display_expression = ""
            self.result_displayed = True
        else:
            self.formula.setText(format_number_with_commas(self.display_expression))
            self.current_input = result
            self.result_displayed = True
            self.update_display()
            
    # 실제 계산 처리 메서드
    def evaluate_expression(self):
        expr = preprocess_expression(self.display_expression)  # 음수 괄호 제거
        tokens = split_expression(expr)

        i = 0
        while i < len(tokens):
            if tokens[i] == "%":
                if i == 0:
                    raise ValueError("잘못된 수식입니다: % 앞에 숫자가 없습니다.")
                try:
                    percent_value = float(tokens[i - 1]) / 100
                    tokens[i - 1] = str(percent_value)
                    tokens.pop(i)
                    i -= 1
                except ValueError:
                    raise ValueError("잘못된 수식입니다: % 앞의 값이 숫자가 아닙니다.")
            i += 1

        try:
            if not tokens:
                return "0"

            result = float(tokens[0])

            i = 1
            while i < len(tokens):
                op = tokens[i]

                try:
                    num = float(tokens[i + 1])
                except (ValueError, IndexError):
                    raise ValueError("잘못된 수식입니다.")

                if op == "+":
                    result = self.add(result, num)
                elif op == "-":
                    result = self.subtract(result, num)
                elif op == "×":
                    result = self.multiply(result, num)
                elif op == "÷":
                    result = self.divide(result, num)


                i += 2

            if result > 1e308 or result < -1e308:
                raise OverflowError("수학적 범위를 초과했습니다.")

            final_result = str(int(result)) if result.is_integer() else format(round(result, 6), ".15g")
            print(f"Final result: {final_result}")  # 최종 결과
            return final_result

        except ZeroDivisionError:
            return "DIV_ZERO"
        except OverflowError:
            return "OVERFLOW_ERROR"
        except (ValueError, IndexError):
            return "SYNTAX_ERROR"
        except Exception as e:
            print(f"Error occurred: {e}")  # 예외 발생 시 오류 메시지
            return "Error"


if __name__ == "__main__":
    app = QApplication([])
    calc = Calculator()
    calc.show()
    app.exec_()