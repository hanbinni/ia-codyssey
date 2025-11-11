# ========================
# todo_fastapi_csv.py
# ========================
from fastapi import FastAPI, HTTPException
from typing import Optional

# ------------------------------------------------------------
# FastAPI만 사용한 간단한 CSV 저장 (CRUD 완성)
# ------------------------------------------------------------
from model import TodoItem

app = FastAPI(title='FastAPI-only CSV TODO (CRUD)', version='2.0.0')

CSV_PATH = 'todos.csv'
todo_list: list[dict] = []  # [{'id': '1', 'title': '...', 'note': '...'}, ...]


# -------------------- 내부 유틸 --------------------

def _save_csv() -> None:
    """todo_list를 수동으로 CSV 문자열로 저장"""
    try:
        f = open(CSV_PATH, 'w', encoding='utf-8')
    except Exception:
        # 파일 쓰기 불가 시 조용히 실패
        return
    # 헤더
    f.write('id,title,note\n')
    for item in todo_list:
        # 쉼표(,), 줄바꿈(\n)을 이스케이프 (\, \n) 처리
        id_ = str(item.get('id', '')).replace(',', '\\,').replace('\n', '\\n')
        title = str(item.get('title', '')).replace(',', '\\,').replace('\n', '\\n')
        note = str(item.get('note', '')).replace(',', '\\,').replace('\n', '\\n')
        f.write(f'{id_},{title},{note}\n')
    f.close()


def _load_csv() -> None:
    """CSV 파일을 수동으로 읽어 todo_list로 로드"""
    try:
        f = open(CSV_PATH, 'r', encoding='utf-8')
    except Exception:
        return
    lines = f.readlines()
    f.close()

    if not lines:
        return
    # 첫 줄 헤더 제거
    for line in lines[1:]:
        line = line.rstrip('\n')
        if not line:
            continue

        parts = []
        cur = ''
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '\\' and i + 1 < len(line):
                nxt = line[i + 1]
                if nxt == ',':
                    cur += ','
                    i += 2
                    continue
                elif nxt == 'n':
                    cur += '\n'
                    i += 2
                    continue
            if ch == ',':
                parts.append(cur)
                cur = ''
                i += 1
                continue
            cur += ch
            i += 1
        parts.append(cur)

        if len(parts) < 3:
            continue
        # 로드 시점에 이스케이프 처리된 문자열을 복원할 필요 없이 그대로 저장
        todo_list.append({'id': parts[0], 'title': parts[1], 'note': parts[2]})


def _next_id() -> str:
    """현재 todo_list의 길이를 기반으로 다음 ID를 반환"""
    # 주의: 실제 환경에서는 UUID나 DB 시퀀스를 사용해야 충돌이 없습니다.
    if not todo_list:
        return '1'
    # 가장 큰 ID를 찾아 +1
    max_id = 0
    for item in todo_list:
        try:
            max_id = max(max_id, int(item.get('id', 0)))
        except ValueError:
            pass  # 숫자가 아닌 ID는 무시
    return str(max_id + 1)


def _find_index_by_id(todo_id: str) -> Optional[int]:
    """ID에 해당하는 항목의 인덱스를 찾아 반환"""
    for idx, item in enumerate(todo_list):
        if item.get('id') == todo_id:
            return idx
    return None


# -------------------- 라우트 --------------------

@app.on_event('startup')
def _startup():
    """앱 시작 시 CSV 파일에서 데이터를 로드"""
    _load_csv()


@app.post('/todo/add')
def add_todo(item: dict):
    if not item:
        raise HTTPException(status_code=400, detail='빈 Dict 는 허용되지 않습니다.')
    # title 키의 존재 여부와 타입 체크를 강화했습니다.
    title = item.get('title')
    if not isinstance(title, str) or not title.strip():
        raise HTTPException(status_code=400, detail='title 키(비어있지 않은 문자열)가 필요합니다.')

    new_id = _next_id()
    note = item.get('note', '')
    todo = {'id': new_id, 'title': str(title), 'note': str(note)}
    todo_list.append(todo)
    _save_csv()
    return {'ok': True, 'id': new_id, 'count': len(todo_list)}


@app.get('/todo/list')
def retrieve_todo():
    """전체 할 일 목록 조회"""
    return {'ok': True, 'count': len(todo_list), 'todos': todo_list}


@app.get('/todo/{todo_id}')
def get_single_todo(todo_id: str):
    """
    개별 할 일 항목 조회
    - 경로 매개변수: todo_id
    """
    idx = _find_index_by_id(todo_id)
    if idx is None:
        raise HTTPException(status_code=404, detail=f'ID {todo_id}에 해당하는 항목이 없습니다.')
    return {'ok': True, 'todo': todo_list[idx]}


@app.put('/todo/{todo_id}')
def update_todo(todo_id: str, payload: TodoItem):
    """
    할 일 항목 수정
    - 경로 매개변수: todo_id
    - 요청 본문: TodoItem (title: str 필수, note: Optional[str])
    """
    idx = _find_index_by_id(todo_id)
    if idx is None:
        raise HTTPException(status_code=404, detail=f'ID {todo_id}에 해당하는 항목이 없습니다.')

    # 모델(payload)에서 받은 데이터로 업데이트
    todo_list[idx]['title'] = payload.title
    # note가 None일 경우 빈 문자열로 저장
    todo_list[idx]['note'] = payload.note or ''

    _save_csv()
    return {'ok': True, 'todo': todo_list[idx]}


@app.delete('/todo/{todo_id}')
def delete_single_todo(todo_id: str):
    """
    할 일 항목 삭제
    - 경로 매개변수: todo_id
    """
    idx = _find_index_by_id(todo_id)
    if idx is None:
        raise HTTPException(status_code=404, detail=f'ID {todo_id}에 해당하는 항목이 없습니다.')

    removed = todo_list.pop(idx)
    _save_csv()
    return {'ok': True, 'deleted': removed}


if __name__ == '__main__':
    print('Run with: uvicorn todo_fastapi_csv:app --reload')