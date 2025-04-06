import time
from datetime import datetime
from week3 import DummySensor 

LOG_FILE_NAME = "sensor_data.log"

class MissionComputer:
    def __init__(self):
        self.env_values = {
            "mars_base_internal_temperature": 0.00,
            "mars_base_external_temperature": 0.00,
            "mars_base_internal_humidity": 0.00,
            "mars_base_external_illuminance": 0.00,
            "mars_base_internal_co2": 0.00,
            "mars_base_internal_oxygen": 0.00
        }
        self.ds = DummySensor()
        self.history = {key: [] for key in self.env_values}

    def get_sensor_data(self):
        cycle_count = 0

        while True:
            try:
                self.env_values = self.ds.set_env()
            except Exception as e:
                print(f"센서 데이터를 가져오는 중 오류 발생: {e}")
                continue

            # 현재 센서 값 출력
            print("{")
            keys = list(self.env_values.keys())
            for i, key in enumerate(keys):
                value = self.env_values[key]
                self.history[key].append(value)
                comma = "," if i < len(keys) - 1 else ""
                print(f'  "{key}": {value}{comma}')
            print("}\n")

            cycle_count += 1

            if cycle_count == 60:  # 5분 경과
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_lines = []

                print("5분 평균 센서 데이터:")
                print("{")
                for i, key in enumerate(keys):
                    values = self.history[key]
                    avg = round(sum(values) / len(values), 2)
                    comma = "," if i < len(keys) - 1 else ""
                    print(f'  "{key}": {avg}{comma}')
                    log_lines.append(f"{now},INFO,{key} 5분 평균: {avg}")
                print("}\n")

                # 로그 저장 (UTF-8)
                try:
                    with open(LOG_FILE_NAME, "a", encoding="utf-8") as log_file:
                        log_file.write("\n".join(log_lines) + "\n")
                except Exception as e:
                    print(f"[오류] 로그 파일 저장 중 문제 발생: {e}")

                # 초기화
                self.history = {key: [] for key in self.env_values}
                cycle_count = 0

            time.sleep(5)

# 실행
if __name__ == "__main__":
    try:
        RunComputer = MissionComputer()
        RunComputer.get_sensor_data()
    except KeyboardInterrupt:
        print("\nSystem stopped…")
