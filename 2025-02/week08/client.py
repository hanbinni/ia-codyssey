# client_cli.py  (표준 라이브러리만)
import json, sys, urllib.request, urllib.error

BASE = "http://127.0.0.1:8000/todo"
TIMEOUT = 5

def _req(path, method="GET", data=None):
    body = None if data is None else json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            s = resp.read().decode("utf-8")
            return json.loads(s) if s else {}
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        try:
            detail = json.loads(msg).get("detail", msg)
        except Exception:
            detail = msg
        print(f"[HTTP {e.code}] {detail}")
    except urllib.error.URLError as e:
        print("[연결 오류] 서버 확인:", e)
    return None

def list_():
    r = _req("/list")
    if not r: return
    print("\n== TODO 목록 ==")
    for t in r.get("todos", []):
        print(f"- [{t['id']}] {t['title']}  ({t.get('note','')})")
    print()

def add_():
    title = input("제목: ").strip()
    if not title:
        print("제목은 필수입니다."); return
    note = input("메모(선택): ").strip()
    r = _req("/add", "POST", {"title": title, "note": note})
    if r: print("추가 완료, ID:", r.get("id"))

def get_():
    tid = input("조회 ID: ").strip()
    r = _req(f"/{tid}")
    if r: print(r)

def update_():
    tid = input("수정 ID: ").strip()
    title = input("새 제목: ").strip()
    if not title:
        print("제목은 필수입니다."); return
    note = input("새 메모(선택): ").strip() or None
    r = _req(f"/{tid}", "PUT", {"title": title, "note": note})
    if r: print("수정 완료")

def delete_():
    tid = input("삭제 ID: ").strip()
    r = _req(f"/{tid}", "DELETE")
    if r: print("삭제 완료")

def main():
    menu = {
        "1": ("목록", list_),
        "2": ("추가", add_),
        "3": ("개별조회", get_),
        "4": ("수정", update_),
        "5": ("삭제", delete_),
        "0": ("종료", lambda: sys.exit(0)),
    }
    while True:
        print("\n[1]목록  [2]추가  [3]개별조회  [4]수정  [5]삭제  [0]종료")
        sel = input("> ").strip()
        action = menu.get(sel)
        if action: action[1]()
        else: print("메뉴를 다시 선택하세요.")

if __name__ == "__main__":
    main()
