
## 📝 수행 과제
1. KBS [뉴스 메인 페이지](http://news.kbs.co.kr)에 접속한다.  
2. 주요 헤드라인 뉴스들을 확인한다.  
3. `beautifulsoup4` 패키지를 설치한다.  
   ```bash
   pip install beautifulsoup4 requests requests-html
   ```
4. 웹 브라우저 개발자 도구를 사용해서 가져올 헤드라인 뉴스의 고유한 값을 찾는다.  
   - 예: `.main-news-wrapper p.title`, `.small-sub-news-wrapper p.title`  
5. **BeautifulSoup의 주요 기능들** (`select`, `get_text`, `attrs`)을 사용해서 헤드라인 뉴스를 가져온다.  
6. 가져온 뉴스들을 **List 객체**에 저장한다.  
7. List 객체를 화면에 출력한다.  
8. 최종적으로 완성된 소스를 `crawling_KBS.py`로 저장한다.  

---

## 🖥️ 코드 실행 예시
```bash
python crawling_KBS.py
```

## ✅ 배운 점
- 단순 문자열 파싱보다 **HTML 구조를 기반으로 원하는 태그를 선택**하는 것이 훨씬 효율적이다.  
- BeautifulSoup의 `select`, `find_all`, `get_text` 같은 기능을 사용하면 재활용성이 높은 크롤러를 작성할 수 있다.  
- 동적 렌더링 페이지의 경우, `requests_html`을 이용해 자바스크립트 실행 후의 DOM을 가져와야 한다는 점도 알게 되었다.  

---
