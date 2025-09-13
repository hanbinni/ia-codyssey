import time
from datetime import datetime, timedelta

# 설정 상수
DEFAULT_LOG_FILE_NAME = "sensor_data.log"
SENSOR_INTERVAL = 5       # 센서 데이터 수집 주기 (초)
LOG_INTERVAL = 15     # 로그 저장 주기 (초)
CYCLES_PER_LOG = LOG_INTERVAL // SENSOR_INTERVAL

class MissionComputer:
    def __init__(self, sensor, log_file_name=DEFAULT_LOG_FILE_NAME):
        self.env_values = {
            "mars_base_internal_temperature": 0.00,
            "mars_base_external_temperature": 0.00,
            "mars_base_internal_humidity": 0.00,
            "mars_base_external_illuminance": 0.00,
            "mars_base_internal_co2": 0.00,
            "mars_base_internal_oxygen": 0.00
        }
        self.ds = sensor
        self.history = {key: [] for key in self.env_values}
        self.log_file_name = log_file_name

    def get_sensor_data(self):
        cycle_count = 0

        while True:
            if self.read_sensor_data():
                self.display_current_values(cycle_count)
                cycle_count += 1

                if cycle_count == CYCLES_PER_LOG:
                    self.log_average_values()
                    self.reset_history()
                    cycle_count = 0

            time.sleep(SENSOR_INTERVAL)

    def read_sensor_data(self):
        try:
            data = self.ds.set_env()

            if not isinstance(data, dict):
                raise ValueError("센서 데이터는 딕셔너리여야 합니다.")

            valid_data = {}

            for key, default_value in self.env_values.items():
                if key not in data:
                    print(f"[경고] '{key}' 값이 누락되어 기본값({default_value})으로 대체됩니다.")
                    valid_data[key] = default_value
                elif not isinstance(data[key], (int, float)):
                    print(f"[경고] '{key}' 값의 타입이 잘못되어 기본값({default_value})으로 대체됩니다. 받은 값: {data[key]}")
                    valid_data[key] = default_value
                else:
                    valid_data[key] = float(data[key])

            unexpected_keys = set(data.keys()) - set(self.env_values.keys())
            if unexpected_keys:
                print(f"[정보] 사용되지 않은 센서 키: {unexpected_keys}")

            self.env_values = valid_data
            for key, value in valid_data.items():
                self.history[key].append(value)

            return True

        except Exception as e:
            print(f"[센서 오류] {e}")
            return False

    def display_current_values(self, cycle_count):
        now = datetime.now()
        print(f"[현재 시간] {now.strftime('%Y-%m-%d %H:%M:%S')}")

        if cycle_count < CYCLES_PER_LOG - 1:
            next_log_time = now + timedelta(seconds=(CYCLES_PER_LOG - cycle_count - 1) * SENSOR_INTERVAL)
            print(f"[다음 로그 저장 예정 시각] {next_log_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[이번 주기에 로그가 저장됩니다. 데이터를 확인하세요]")

        print("{")
        keys = list(self.env_values.keys())
        for i, key in enumerate(keys):
            value = self.env_values[key]
            comma = "," if i < len(keys) - 1 else ""
            print(f'  "{key}": {value}{comma}')
        print("}\n")

    def log_average_values(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_lines = []

        interval_str = f"{LOG_INTERVAL // 60}분" if LOG_INTERVAL >= 60 else f"{LOG_INTERVAL}초"
        print(f"{interval_str} 평균 센서 데이터:")
        print("{")
        keys = list(self.history.keys())
        for i, key in enumerate(keys):
            values = self.history[key]
            avg = round(sum(values) / len(values), 2)
            comma = "," if i < len(keys) - 1 else ""
            print(f'  "{key}": {avg}{comma}')
            log_lines.append(f"{now},INFO,{key} {interval_str} 평균: {avg}")
        print("}\n")

        self.log_to_file(log_lines)

    def log_to_file(self, lines):
        try:
            with open(self.log_file_name, "a", encoding="utf-8") as log_file:
                log_file.write("\n".join(lines) + "\n")
        except Exception as e:
            print(f"[오류] 로그 파일 저장 중 문제 발생: {e}")

    def reset_history(self):
        self.history = {key: [] for key in self.env_values}

# 실행부
if __name__ == "__main__":
    from week03 import DummySensor

    try:
        dummy_sensor = DummySensor()
        RunComputer = MissionComputer(sensor=dummy_sensor)
        RunComputer.get_sensor_data()
    except KeyboardInterrupt:
        print("\nSystem stopped…")
