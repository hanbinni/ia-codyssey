from fastapi import FastAPI, HTTPException

# ------------------------------------------------------------
# FastAPI만 사용한 간단한 CSV 저장
# (표준 csv/json/os 등 라이브러리 전혀 import 안 함)
# ------------------------------------------------------------

app = FastAPI(title='FastAPI-only CSV TODO', version='1.0.0')

CSV_PATH = 'todos.csv'
todo_list = []  # [{'id': '1', 'title': '...', 'note': '...'}, ...]

# -------------------- 내부 유틸 --------------------

def _save_csv():
    """todo_list를 수동으로 CSV 문자열로 저장"""
    try:
        f = open(CSV_PATH, 'w', encoding='utf-8')
    except Exception:
        # 파일 쓰기 불가 시 조용히 실패
        return
    # 헤더
    f.write('id,title,note\n')
    for item in todo_list:
        # 쉼표, 줄바꿈이 들어가면 이스케이프
        id_ = str(item.get('id', '')).replace(',', '\\,').replace('\n', '\\n')
        title = str(item.get('title', '')).replace(',', '\\,').replace('\n', '\\n')
        note = str(item.get('note', '')).replace(',', '\\,').replace('\n', '\\n')
        f.write(f'{id_},{title},{note}\n')
    f.close()


def _load_csv():
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
        # 콤마 단위로 나누되, \,는 복원
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
        todo_list.append({'id': parts[0], 'title': parts[1], 'note': parts[2]})


def _next_id() -> str:
    return str(len(todo_list) + 1)


# -------------------- 라우트 --------------------

@app.on_event('startup')
def _startup():
    _load_csv()


@app.post('/todo/add')
def add_todo(item: dict):
    if not item:
        raise HTTPException(status_code=400, detail='빈 Dict 는 허용되지 않습니다.')
    if 'title' not in item:
        raise HTTPException(status_code=400, detail='title 키가 필요합니다.')

    new_id = _next_id()
    note = item.get('note', '')
    todo = {'id': new_id, 'title': str(item['title']), 'note': str(note)}
    todo_list.append(todo)
    _save_csv()
    return {'ok': True, 'id': new_id, 'count': len(todo_list)}


@app.get('/todo/list')
def retrieve_todo():
    return {'ok': True, 'count': len(todo_list), 'todos': todo_list}


if __name__ == '__main__':
    print('Run with: uvicorn todo_fastapi_csv:app --reload')
