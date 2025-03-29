import random
from datetime import datetime

LOG_FILE_NAME = "sensor_data.log"

class DummySensor:
    def __init__(self):
        """더미 데이터 초기화"""
        self.env_values = {
            "mars_base_internal_temperature": 0.0,
            "mars_base_external_temperature": 0.0,
            "mars_base_internal_humidity": 0.0,
            "mars_base_external_illuminance": 0.0,
            "mars_base_internal_co2": 0.0,
            "mars_base_internal_oxygen": 0.0
        }

        # 로그 파일이 존재하는지 확인하고, 없으면 헤더 추가
        try:
            with open(LOG_FILE_NAME, "r+") as log_file:
                first_line = log_file.readline().strip()  # 첫 줄 읽기
                if not first_line:  # 파일이 비어 있으면 헤더 추가
                    log_file.write("timestamp,event,message\n")
        except FileNotFoundError:
            with open(LOG_FILE_NAME, "w") as log_file:
                log_file.write("timestamp,event,message\n")

    def set_env(self):
        """랜덤 환경 데이터 설정"""
        self.env_values = {
            "mars_base_internal_temperature": round(random.uniform(18, 30), 2),
            "mars_base_external_temperature": round(random.uniform(0, 21), 2),
            "mars_base_internal_humidity": round(random.uniform(50, 60), 2),
            "mars_base_external_illuminance": round(random.uniform(500, 715), 2),
            "mars_base_internal_co2": round(random.uniform(0.02, 0.1), 2),
            "mars_base_internal_oxygen": round(random.uniform(4, 7), 2)
        }

    def get_env(self):
        """현재 환경 값을 로그 파일에 저장"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_messages = [
            f"{current_time},INFO,{key}: {value}"
            for key, value in self.env_values.items()
        ]

        try:
            with open(LOG_FILE_NAME, "a") as log_file:
                for message in log_messages:
                    log_file.write(message + "\n")
        except Exception as e:
            print(f"파일 쓰기 오류: {e}")

        return self.env_values

# 클래스 인스턴스화
ds = DummySensor()

# 환경 데이터 설정
ds.set_env()

# 환경 값 출력 및 자동 로그 저장
for key, value in ds.get_env().items():
    print(f"{key}: {value}")
