# crawling_KBS.py

from requests_html import HTMLSession
from bs4 import BeautifulSoup

BASE_URL = "http://news.kbs.co.kr"

def crawl_kbs_headlines():
    """KBS 메인 페이지에서 헤드라인 뉴스(메인+서브)를 크롤링"""

    session = HTMLSession()
    r = session.get(BASE_URL)

    # JS 실행 (동적 렌더링 처리)
    r.html.render(timeout=30, sleep=5)

    soup = BeautifulSoup(r.html.html, "html.parser")

    # 메인 헤드라인 (main-news-wrapper)
    main_news = []
    for box in soup.select(".main-news-wrapper a.main-news"):
        title = box.select_one("p.title").get_text(strip=True) if box.select_one("p.title") else ""
        desc = box.select_one("p.news-txt").get_text(strip=True) if box.select_one("p.news-txt") else ""
        link = BASE_URL + box.get("href", "")
        main_news.append({"title": title, "desc": desc, "link": link})

    # 서브 헤드라인 (small-sub-news-wrapper)
    sub_news = []
    for box in soup.select(".small-sub-news-wrapper a"):
        title = box.select_one("p.title").get_text(strip=True) if box.select_one("p.title") else ""
        link = BASE_URL + box.get("href", "")
        sub_news.append({"title": title, "desc": "", "link": link})

    return main_news + sub_news


if __name__ == "__main__":
    headlines = crawl_kbs_headlines()

    print("📌 KBS 주요 헤드라인 뉴스\n")
    for i, news in enumerate(headlines, 1):
        print(f"{i}. {news['title']}")
        if news['desc']:
            print(f"   └ 요약: {news['desc']}")
        print(f"   └ 링크: {news['link']}\n")
