# crawling_weather.py

import requests
from bs4 import BeautifulSoup

def crawl_weather():
    """네이버 날씨에서 현재 서울 날씨 정보를 크롤링"""
    url = "https://search.naver.com/search.naver?query=서울+날씨"
    res = requests.get(url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    # 현재 기온
    temp = soup.select_one(".temperature_text").get_text(strip=True)
    # 날씨 상태 (흐림, 맑음 등)
    cast = soup.select_one(".temperature_info .summary").get_text(strip=True)

    return {"temp": temp, "cast": cast}


if __name__ == "__main__":
    weather = crawl_weather()
    print("🌦️ 오늘의 서울 날씨")
    print(f"- 현재 기온: {weather['temp']}")
    print(f"- 상태: {weather['cast']}")
