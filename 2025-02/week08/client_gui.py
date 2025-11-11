# client_pyqt_polished.py
# pip install PyQt5
import sys, json, urllib.request, urllib.error
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit, QPushButton, QMessageBox,
    QLabel, QSplitter, QFrame, QMenu, QAction, QShortcut
)

# ==== 설정 ====
BASE = "http://127.0.0.1:8000/todo"   # 서버 포트 맞춰 수정 (예: 8001이면 ...8001/todo)
TIMEOUT = 5


# ==== HTTP 공통 함수 ====
def http_req(path: str, method: str = "GET", data: dict | None = None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="ignore")
        try:
            detail = json.loads(raw).get("detail", raw)
        except Exception:
            detail = raw
        QMessageBox.critical(None, "HTTP 오류", f"{e.code}: {detail}")
    except urllib.error.URLError:
        QMessageBox.critical(None, "연결 오류", "서버가 실행 중인지, BASE 주소/포트가 맞는지 확인하세요.")
    except Exception as e:
        QMessageBox.critical(None, "알 수 없는 오류", str(e))
    return None


# ==== 메인 앱 ====
class TodoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastAPI Todo (PyQt5)")
        self.resize(980, 600)

        self.items: list[dict] = []
        self.selected_id: str | None = None
        self.last_filter: str = ""

        self._build_ui()
        self._wire_events()
        self.load()

    # ---------- UI 구성 ----------
    def _build_ui(self):
        # 다크 테마 스타일
        self.setStyleSheet("""
            QWidget { background: #1f1f1f; color: #eaeaea; font-size: 14px; }
            QListWidget { border: 1px solid #3a3a3a; border-radius: 10px; padding: 6px; }
            QLineEdit, QTextEdit {
                background: #2a2a2a; border: 1px solid #444; border-radius: 8px; padding: 10px;
                color: #ffffff; selection-background-color: #3c6df0;
            }
            QTextEdit { min-height: 160px; }
            QGroupBox { border: 1px solid #333; border-radius: 12px; margin-top: 16px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; }
            QPushButton {
                background: #2d2f38; border: 1px solid #444; border-radius: 10px; padding: 10px 16px;
            }
            QPushButton:hover { background: #3a3d48; }
            QPushButton:pressed { background: #2a2c34; }
            QPushButton:disabled { color: #7a7a7a; border-color: #3a3a3a; }
            #PrimaryBtn { background: #3c6df0; border: none; color: white; }
            #PrimaryBtn:hover { background: #2f5de0; }
            #DangerBtn { background: #cc3d3d; border: none; color: white; }
            #DangerBtn:hover { background: #bb2f2f; }
            #Header { font-size: 16px; color: #cfcfcf; }
            #StatusBar { color: #a0a0a0; font-size: 12px; }
            QFrame#line { background: #2c2c2c; max-height: 1px; min-height: 1px; }
        """)

        splitter = QSplitter(Qt.Horizontal, self)

        # --- Left: 목록 영역(폭 줄임) ---
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 12, 12, 12)

        header = QLabel("할 일 목록")
        header.setObjectName("Header")

        self.search = QLineEdit()
        self.search.setPlaceholderText("검색(제목 포함) ... Enter")
        self.list = QListWidget()
        self.list.setAlternatingRowColors(True)
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)

        left_layout.addWidget(header)
        left_layout.addWidget(self.search)
        left_layout.addSpacing(6)
        left_layout.addWidget(self.list)

        # --- Right: 입력 폼(제목 + 메모 크게) ---
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 12, 12, 12)

        form_group = QGroupBox("항목 추가/수정")
        form = QFormLayout(form_group)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(14)

        self.title = QLineEdit()
        self.title.setPlaceholderText("제목을 입력하세요 (필수)")
        self.note = QTextEdit()
        self.note.setPlaceholderText("메모(선택). 여러 줄 작성 가능")

        form.addRow("제목", self.title)
        form.addRow("메모", self.note)

        # 버튼들
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("추가")
        self.btn_add.setObjectName("PrimaryBtn")
        self.btn_update = QPushButton("수정")
        self.btn_delete = QPushButton("삭제")
        self.btn_delete.setObjectName("DangerBtn")
        self.btn_refresh = QPushButton("새로고침")

        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)

        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_update)
        btn_row.addWidget(self.btn_delete)
        btn_row.addStretch(1)
        btn_row.addWidget(self.btn_refresh)

        # 상태 라인
        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        self.status = QLabel("Ready")
        self.status.setObjectName("StatusBar")

        right_layout.addWidget(form_group)
        right_layout.addSpacing(10)
        right_layout.addLayout(btn_row)
        right_layout.addSpacing(8)
        right_layout.addWidget(line)
        right_layout.addWidget(self.status)

        splitter.addWidget(left)
        splitter.addWidget(right)

        # 왼쪽(목록) 폭을 줄이고 오른쪽 폼을 크게
        splitter.setSizes([360, 620])

        # 루트 레이아웃
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.addWidget(splitter)

    # ---------- 이벤트 바인딩 ----------
    def _wire_events(self):
        # 버튼/리스트
        self.list.currentRowChanged.connect(self.on_select)
        self.list.customContextMenuRequested.connect(self.show_context_menu)
        self.btn_add.clicked.connect(self.on_add)
        self.btn_update.clicked.connect(self.on_update)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_refresh.clicked.connect(self.load)

        # 검색
        self.search.returnPressed.connect(self.apply_filter)

        # 편의 단축키
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self.title.setFocus)  # 새로 입력
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self.on_update)       # 저장(수정)
        QShortcut(QKeySequence("Delete"), self, activated=self.on_delete)       # 삭제
        QShortcut(QKeySequence("F5"), self, activated=self.load)                # 새로고침
        # 입력에서 Enter 처리
        self.title.returnPressed.connect(self.on_add)

    # ---------- 데이터 로딩/필터 ----------
    def load(self):
        self.status.setText("서버에서 목록을 가져오는 중…")
        self.list.clear()
        resp = http_req("/list")
        self.items = (resp or {}).get("todos", []) if resp is not None else []
        for it in self.items:
            txt = self._format_item_text(it)
            self.list.addItem(QListWidgetItem(txt))
        self.clear_inputs()
        self.status.setText(f"총 {len(self.items)}개")
        # 기존 필터가 있으면 유지
        if self.last_filter:
            self.apply_filter()

    def apply_filter(self):
        key = self.search.text().strip().lower()
        self.last_filter = key
        self.list.clear()
        shown = 0
        for it in self.items:
            title = it.get("title", "")
            if key and key not in title.lower():
                continue
            self.list.addItem(QListWidgetItem(self._format_item_text(it)))
            shown += 1
        self.clear_inputs()
        self.status.setText(f"필터 결과: {shown}개")

    def _format_item_text(self, it: dict) -> str:
        s = f"[{it.get('id','')}] {it.get('title','')}"
        note = it.get("note")
        if note:
            s += f" ({note[:40]}...)" if len(note) > 40 else f" ({note})"
        return s

    # ---------- 선택/입력 상태 ----------
    def clear_inputs(self):
        self.selected_id = None
        self.title.clear()
        self.note.clear()
        self.btn_update.setEnabled(False)
        self.btn_delete.setEnabled(False)

    def on_select(self, row: int):
        if row < 0:
            self.clear_inputs()
            return
        text = self.list.item(row).text()
        # 텍스트 형식: [id] title (note...)
        try:
            id_part = text.split("]")[0][1:]
        except Exception:
            self.clear_inputs(); return
        it = next((x for x in self.items if x.get("id") == id_part), None)
        if not it:
            self.clear_inputs(); return

        self.selected_id = it["id"]
        self.title.setText(it.get("title", ""))
        self.note.setPlainText(it.get("note", "") or "")
        self.btn_update.setEnabled(True)
        self.btn_delete.setEnabled(True)
        self.status.setText(f"선택: ID {self.selected_id}")

    # ---------- 액션 ----------
    def on_add(self):
        t = self.title.text().strip()
        if not t:
            QMessageBox.warning(self, "경고", "제목은 필수입니다.")
            self.title.setFocus()
            return
        n = self.note.toPlainText().strip()
        r = http_req("/add", "POST", {"title": t, "note": n})
        if r:
            self.status.setText("추가 완료")
            self.load()
            # UX: 바로 다시 제목 입력으로 포커스
            QTimer.singleShot(0, self.title.setFocus)

    def on_update(self):
        if not self.selected_id:
            QMessageBox.warning(self, "경고", "수정할 항목을 선택하세요.")
            return
        t = self.title.text().strip()
        if not t:
            QMessageBox.warning(self, "경고", "제목은 필수입니다.")
            self.title.setFocus()
            return
        n = self.note.toPlainText().strip() or None
        r = http_req(f"/{self.selected_id}", "PUT", {"title": t, "note": n})
        if r:
            self.status.setText(f"수정 완료 (ID {self.selected_id})")
            self.load()

    def on_delete(self):
        if not self.selected_id:
            return
        if QMessageBox.question(self, "확인", f"ID {self.selected_id} 항목을 삭제하시겠습니까?",
                                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return
        r = http_req(f"/{self.selected_id}", "DELETE")
        if r:
            self.status.setText(f"삭제 완료 (ID {self.selected_id})")
            self.load()

    # ---------- 리스트 컨텍스트 메뉴 ----------
    def show_context_menu(self, pos):
        if self.list.count() == 0:
            return
        menu = QMenu(self)
        act_copy_id = QAction("ID 복사", self)
        act_delete = QAction("삭제", self)
        menu.addAction(act_copy_id)
        menu.addSeparator()
        menu.addAction(act_delete)

        action = menu.exec_(self.list.mapToGlobal(pos))
        row = self.list.currentRow()
        if row < 0:
            return
        if action == act_copy_id:
            # 현재 표시 텍스트에서 ID만 추출
            text = self.list.item(row).text()
            try:
                id_part = text.split("]")[0][1:]
            except Exception:
                return
            QApplication.clipboard().setText(id_part)
            self.status.setText(f"ID 복사됨: {id_part}")
        elif action == act_delete:
            self.on_delete()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TodoApp()
    w.show()
    sys.exit(app.exec_())
