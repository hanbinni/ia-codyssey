from pydantic import BaseModel
from typing import Optional


class TodoItem(BaseModel):
    """수정(UPDATE)용 데이터 모델.
    - 제목(title)은 필수입니다.
    - 메모(note)는 선택 사항입니다.
    """
    title: str
    note: Optional[str] = None