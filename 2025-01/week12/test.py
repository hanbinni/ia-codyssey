import pandas as pd
import mysql.connector
from mysql.connector import Error

# CSV 파일 경로
csv_file = "mars_weathers_data.csv"

# CSV 파일 읽기
df = pd.read_csv(csv_file)

# ① CSV 미리보기
print("📄 [CSV 미리보기] 상위 10줄:")
print(df.head(10))

# ② 정보 출력
print("\n📊 [데이터 요약 정보]")
print(f"✅ 총 행 개수: {len(df)}")
print(f"✅ 컬럼 목록: {list(df.columns)}")
print("\n📋 데이터 타입:\n", df.dtypes)

# ③ 사용자 입력 받기
confirm = input("\n📥 이 데이터를 DB에 삽입하시겠습니까? (y/n): ").strip().lower()

if confirm != 'y':
    print("⛔️ 삽입이 취소되었습니다.")
    exit()

# ④ MySQL 연결 정보
config = {
    "host": "localhost",
    "user": "root",
    "password": "rootroot",  # ← 실제 비밀번호로 바꿔주세요
    "database": "weather_db"
}

# ⑤ 데이터 삽입 시도
try:
    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    for _, row in df.iterrows():
        sql = """
        INSERT INTO mars_weather (mars_date, temp, storm)
        VALUES (%s, %s, %s)
        """
        values = (row['mars_date'], int(row['temp']), int(row['storm']))
        cursor.execute(sql, values)

    connection.commit()
    print(f"✅ {len(df)}개의 행이 mars_weather 테이블에 삽입되었습니다.")

except Error as e:
    print("❌ 오류 발생:", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("🔒 DB 연결 종료됨")
