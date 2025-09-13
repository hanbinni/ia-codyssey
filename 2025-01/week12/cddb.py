# DB에 테이블을 생성하는 코드

import mysql.connector
from mysql.connector import Error

# ================== 설정 ==================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "rootroot",
    "database": "weather_db"
}

CREATE_DB_NAME = "weather_db"

CREATE_TABLE_QUERY = """
CREATE TABLE mars_weather (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    mars_date DATETIME NOT NULL,
    temp INT,
    storm INT
)
"""

# ================== 로그 유틸 ==================
def write_log(message, level="INFO"):
    full_message = f"[{level}] {message}"
    print(full_message)
    with open("db_setup.log", "a", encoding="utf-8") as f:
        f.write(full_message + "\n")

# ================== 사용자 입력 ==================
def ask_user(prompt="계속 진행하시겠습니까?"):
    while True:
        answer = input(prompt + " [y/N]: ").strip().lower()
        if answer in ["y", "yes"]:
            return True
        elif answer in ["n", "no", ""]:
            return False
        else:
            print("⚠️ 유효하지 않은 입력입니다. y 또는 n으로 답해주세요.")

# ================== DB 연결 관련 ==================
def create_raw_connection():
    try:
        return mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
    except Error as e:
        write_log("❌ MySQL 연결 실패 (raw): " + str(e), level="ERROR")
        raise

def create_connection_with_db():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        write_log("❌ MySQL 연결 실패 (with DB): " + str(e), level="ERROR")
        raise

# ================== DB 작업 ==================
def database_exists(connection, db_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists
    except Error as e:
        write_log("❌ DB 존재 여부 확인 실패: " + str(e), level="ERROR")
        raise

def create_database(connection, db_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE {db_name}")
        write_log(f"✅ 데이터베이스 '{db_name}' 생성 완료")
        cursor.close()
    except Error as e:
        write_log("❌ DB 생성 실패: " + str(e), level="ERROR")
        raise

def drop_database(connection, db_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"DROP DATABASE {db_name}")
        write_log(f"🗑️ 데이터베이스 '{db_name}' 삭제 완료")
        cursor.close()
    except Error as e:
        write_log("❌ DB 삭제 실패: " + str(e), level="ERROR")
        raise

# ================== 테이블 작업 ==================
def table_exists(connection, table_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists
    except Error as e:
        write_log("❌ 테이블 존재 여부 확인 실패: " + str(e), level="ERROR")
        raise

def create_table(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        write_log("✅ 테이블 생성 완료")
        cursor.close()
    except Error as e:
        write_log("❌ 테이블 생성 실패: " + str(e), level="ERROR")
        raise

def drop_table(connection, table_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        write_log(f"🗑️ 테이블 '{table_name}' 삭제 완료")
        cursor.close()
    except Error as e:
        write_log("❌ 테이블 삭제 실패: " + str(e), level="ERROR")
        raise

# ================== DB 흐름 처리 ==================
def handle_database():
    try:
        raw_conn = create_raw_connection()
    except Error:
        return

    try:
        while True:
            if database_exists(raw_conn, CREATE_DB_NAME):
                write_log(f"⚠️ 데이터베이스 '{CREATE_DB_NAME}'가 이미 존재합니다.")
                if ask_user("기존 DB를 그대로 사용하시겠습니까?"):
                    write_log("ℹ️ 기존 DB 사용 선택됨")
                    break
                elif ask_user(f"정말로 '{CREATE_DB_NAME}' DB를 삭제하고 새로 생성하시겠습니까? 이 작업은 되돌릴 수 없습니다."):
                    drop_database(raw_conn, CREATE_DB_NAME)
                    create_database(raw_conn, CREATE_DB_NAME)
                    break
                else:
                    write_log("↩️ 이전 질문으로 돌아갑니다.")
            else:
                create_database(raw_conn, CREATE_DB_NAME)
                break
    finally:
        raw_conn.close()

# ================== 테이블 흐름 처리 ==================
def handle_table():
    try:
        conn = create_connection_with_db()
    except Error:
        return

    try:
        while True:
            if table_exists(conn, "mars_weather"):
                write_log("⚠️ 테이블 'mars_weather'가 이미 존재합니다.")
                if ask_user("기존 테이블을 그대로 사용하시겠습니까?"):
                    write_log("⏭️ 테이블 생성 건너뜀")
                    break
                elif ask_user("정말로 'mars_weather' 테이블을 삭제하고 새로 생성하시겠습니까? 이 작업은 되돌릴 수 없습니다."):
                    drop_table(conn, "mars_weather")
                    create_table(conn, CREATE_TABLE_QUERY)
                    break
                else:
                    write_log("↩️ 이전 질문으로 돌아갑니다.")
            else:
                create_table(conn, CREATE_TABLE_QUERY)
                break
    finally:
        conn.close()

# ================== 실행 ==================
def main():
    write_log("🚀 DB 및 테이블 생성 프로세스 시작")
    try:
        handle_database()
        handle_table()
    except Error as e:
        write_log(f"❌ 치명적인 오류 발생: {e}", level="ERROR")
    finally:
        write_log("🏁 프로세스 종료")

if __name__ == "__main__":
    main()
