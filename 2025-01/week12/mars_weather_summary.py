import mysql.connector
from mysql.connector import Error

CSV_FILE = "mars_weathers_data.csv"  # CSV 파일 경로
PAGE_SIZE = 10  # 한 페이지에 보여줄 행 수

# DB 접속 정보
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "rootroot",
    "database": "weather_db"
}

# 데이터베이스 연결 및 쿼리 실행(추가과제)
class MySQLHelper:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None

    # DB연결
    def connect(self):
        try:
            self.conn = mysql.connector.connect(**self.config)
            self.cursor = self.conn.cursor()
            return True
        except Error as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            return False
    # 종료
    def close(self):
        """DB 연결 종료"""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()

    # 현제 코드 특화 삽입 쿼리
    def insert_data(self, rows):
        query = "INSERT INTO mars_weather (mars_date, temp, storm) VALUES (%s, %s, %s)"
        success_count = 0
        fail_count = 0

        for row in rows:
            try:
                mars_date = row[1]
                temp = int(float(row[2]))
                storm = int(float(row[3]))
                self.cursor.execute(query, (mars_date, temp, storm))
                success_count += 1
            except (IndexError, ValueError) as e:
                print(f"⚠️ 오류 발생 - 행 무시됨: {row} -> {e}")
                fail_count += 1
            except Error as db_err:
                print(f"❌ DB 오류 - 행 무시됨: {row} -> {db_err}")
                fail_count += 1

        self.conn.commit()
        print(f"\n✅ 삽입 완료: {success_count}건 성공, {fail_count}건 실패")

    #select
    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except Error as e:
            print(f"❌ 쿼리 실행 오류: {e}")
            return []
    # INSERT/UPDATE/DELETE
    def execute_non_query(self, query, params=None):
        try:
            self.cursor.execute(query, params or ())
            self.conn.commit()
        except Error as e:
            print(f"❌ 실행 오류: {e}")


# 파일 로드
def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if not lines:
                print("❌ CSV 파일이 비어 있습니다.")
                return None, []
            headers = lines[0].strip().split(',')
            rows = [line.strip().split(',') for line in lines[1:] if line.strip()]
            return headers, rows
    except FileNotFoundError:
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        print(f"❌ CSV 파일 읽기 오류: {e}")
    return None, []

# 데이터 출력
def display_page(headers, rows, page):
    total = len(rows)
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, total)

    print("\n📋 CSV 헤더:", headers)
    print(f"\n📄 데이터 ({start + 1}~{end} / {total}):")
    for row in rows[start:end]:
        print(row)

    return start, end, total

# 키보드 입력 반환 처리
def get_user_choice(current_page, total):
    options = []
    if current_page > 0:
        options.append(f"P) 이전 {PAGE_SIZE}개")
    if (current_page + 1) * PAGE_SIZE < total:
        options.append(f"N) 다음 {PAGE_SIZE}개")
    options.append("Q) 초기화면으로 돌아가기")

    print("\n옵션: " + " | ".join(options))
    return input("선택: ").strip().lower()

# 데이터 패이지별로 탐색
def browse_data(headers, rows):
    page = 0
    while True:
        start, end, total = display_page(headers, rows, page)
        choice = get_user_choice(page, total)

        if choice == 'n' and end < total:
            page += 1
        elif choice == 'p' and page > 0:
            page -= 1
        elif choice == 'q':
            print("\n↩️ 초기화면으로 돌아갑니다.")
            return
        else:
            print("⚠️ 유효하지 않은 입력입니다.")

# 저장 기능
def insert_all_data(rows):
    """
    CSV 데이터 전체를 DB에 저장
    """
    db = MySQLHelper(DB_CONFIG)
    if db.connect():
        db.insert_data(rows)
        db.close()

# 메뉴 제어
def show_main_menu(headers, rows):
    while True:
        print("\n📦 데이터를 불러왔습니다. 다음 중 하나를 선택하세요:")
        print("1) 확인 (페이지 단위로 보기)")
        print("2) 저장 (DB에 INSERT)")
        print("3) 종료")

        choice = input("선택: ").strip()
        if choice == '1':
            browse_data(headers, rows)
        elif choice == '2':
            insert_all_data(rows)
        elif choice == '3':
            print("\n👋 프로그램을 종료합니다.")
            break
        else:
            print("⚠️ 유효하지 않은 입력입니다. 다시 시도해주세요.")

def main():
    """
    프로그램 진입점
    """
    print("🚀 시스템을 시작합니다...")
    headers, rows = load_data(CSV_FILE)
    if headers and rows:
        show_main_menu(headers, rows)

if __name__ == "__main__":
    main()
