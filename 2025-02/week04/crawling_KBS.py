from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import random

# --- 설정 ---
USER_ID = ""
USER_PW = ""
# ----------

options = webdriver.ChromeOptions()

# 봇 감지 회피 1단계: 크롬 옵션을 통해 자동화 플래그를 숨김
# 웹사이트가 Selenium 자동화 도구에 의해 제어되고 있음을 나타내는
# 내부 플래그(예: 'enable-automation')를 제거합니다.
options.add_experimental_option("excludeSwitches", ["enable-automation"])

# 브라우저 확장을 통해 자동화 도구가 사용되고 있음을 나타내는
# 확장 기능을 비활성화하여 봇 감지를 더욱 어렵게 만듭니다.
options.add_experimental_option('useAutomationExtension', False)

# 브라우저 창을 최대화된 상태로 시작하도록 설정합니다.
# 일반 사용자는 창을 전체 화면으로 보는 경우가 많으므로, 이 또한 자연스러운 행동처럼 보이게 합니다.
options.add_argument("--start-maximized")

# 설정된 옵션(options)을 적용하여 크롬 드라이버 인스턴스를 생성합니다.
driver = webdriver.Chrome(options=options)

# ✅ 로그인 페이지
driver.get("https://nid.naver.com/nidlogin.login")
time.sleep(random.uniform(2.5, 4.5))
print("[LOG] 로그인 페이지 접속")

# 봇 감지 회피 2단계: JavaScript를 사용하여 'webdriver' 속성 숨기기
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
try:
    # 봇 감지 회피 3단계: 렌덤 마우스 움직임
    actions = ActionChains(driver)
    actions.move_by_offset(random.randint(50, 200), random.randint(50, 150)).perform()
    time.sleep(random.uniform(0.5, 1.0))
    print("[LOG] 마우스 움직임 시뮬레이션")

    # 봇 감지 회피 4단계: 아이디 직접 js로 직접 삽입
    js_id = f"document.getElementById('id').value = '{USER_ID}';"
    js_pw = f"document.getElementById('pw').value = '{USER_PW}';"

    driver.execute_script(js_id)
    time.sleep(random.uniform(1.0, 2.0))
    driver.execute_script(js_pw)
    time.sleep(random.uniform(1.0, 2.0))
    # 로그인 버튼 클릭
    driver.find_element(By.ID, "log.login").click()
    time.sleep(random.uniform(5, 7))

except Exception as e:
    print(f"[ERROR] 로그인 과정 중 오류 발생: {e}")
    driver.quit()
    exit()

# ✅ 메일 페이지 이동
driver.get("https://mail.naver.com")
print("[LOG] 메일 페이지 접속, 메일 리스트 로딩 대기 중...")

# ✅ 메일 리스트 로딩 대기 및 아이템 추출
mail_items = []
titles = []
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.mail_list"))
    )
    mail_items = driver.find_elements(By.CSS_SELECTOR, "li.mail_item")
    print(f"[LOG] 메일 아이템 개수: {len(mail_items)}")

    for idx, item in enumerate(mail_items):
        text = ""
        try:
            # CSS 선택자: 'a.mail_title_link' 내부의 'span.text'만 찾음
            title_element = item.find_element(By.CSS_SELECTOR, "a.mail_title_link > span.text")
            text = title_element.text.strip()
            if text:
                titles.append(text)
        except Exception as e:
            continue

except Exception as e:
    print(f"[ERROR] 메일 리스트를 찾을 수 없거나 타임아웃 발생: {e}")

print("\n[RESULT] 최종 메일 제목 리스트:", titles)

driver.quit()
print("[LOG] 브라우저 종료")