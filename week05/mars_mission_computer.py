import platform # 시스템 정보 가져오기
import os # 운영체제 관련 기능
SETTINGS_FILE = 'setting.txt'
class MissionComputer:
    # 4주차 부분 생략 
    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings = self.load_settings(settings_file)

    def load_settings(self, settings_file):
        """설정 파일을 읽고, 항목을 True 또는 False로 로드"""
        settings = {}
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                section = None
                for line in f:
                    line = line.strip()

                    # 공백 줄 또는 주석(#) 무시
                    if not line or line.startswith('#'):
                        continue

                    # 섹션 시작 판별별
                    if line.startswith('[') and line.endswith(']'):
                        section = line.strip('[]')
                        settings[section] = {}
                    # 설정 항목 처리
                    elif '=' in line and section:
                        try:
                            key, value = line.split('=', 1)
                            settings[section][key.strip()] = self.parse_boolean(value.strip())
                        except ValueError:
                            print(f"Invalid line in section [{section}]: {line}") #이상한 형식의 라인 처리
                    else:
                        print(f"Ignored line (no section or invalid format): {line}")#키 값이 없는 경우 처리

        except Exception as e:
            print(f"Error reading settings file: {e}")

        return settings


    def parse_boolean(self, value):#설정값 boolean으로 변환
        """문자열을 True 또는 False로 변환 (대소문자 무시, 다양한 표현 허용)"""
        return value.strip().lower() in ['true', '1', 'yes', 'on']


    def get_mission_computer_info(self):
        """시스템의 기본 정보를 딕셔너리로 반환"""
        system_info = {}

        # 설정 파일을 순회하며 필요한 정보만 반환
        system_info = self.get_system_info(system_info)

        return system_info

    def get_system_info(self, system_info):
        """설정된 항목에 맞춰 시스템 정보를 추가"""
        if self.settings.get('SystemInfo', {}).get("운영체계", False):
            system_info["운영체계"] = platform.system()
        if self.settings.get('SystemInfo', {}).get("운영체계 버전", False):
            system_info["운영체계 버전"] = platform.version()
        if self.settings.get('SystemInfo', {}).get("CPU 타입", False):
            system_info["CPU 타입"] = platform.processor()
        if self.settings.get('SystemInfo', {}).get("CPU 코어 수", False):
            system_info["CPU 코어 수"] = os.cpu_count()
        if self.settings.get('SystemInfo', {}).get("메모리 크기 (GB)", False):
            system_info["메모리 크기 (GB)"] = self.get_memory_size()

        return system_info

    def get_mission_computer_load(self):
        """CPU 및 메모리 사용 정보를 딕셔너리로 반환"""
        load_info = {}
        load_info = self.get_load_info(load_info)

        return load_info

    def get_load_info(self, load_info):
        """설정된 항목에 맞춰 부하 정보를 추가"""
        if self.settings.get('LoadInfo', {}).get("CPU 사용률 (%)", False):
            load_info["CPU 사용률 (%)"] = self.get_cpu_usage()
        if self.settings.get('LoadInfo', {}).get("메모리 사용률 (%)", False):
            load_info["메모리 사용률 (%)"] = self.get_memory_usage()

        return load_info

    def get_memory_size(self):
        """운영체제별 메모리 크기 구하기 (단위: GB)"""
        system = platform.system()
        try:
            if system == "Windows":
                return self.get_memory_size_windows()
            elif system == "Linux":
                return self.get_memory_size_linux()
            elif system == "Darwin":
                return self.get_memory_size_macos()
        except Exception as e:
            print(f"Error fetching memory size: {e}")
            return None

    def get_memory_size_windows(self):
        """Windows에서 메모리 크기 가져오기"""
        result = os.popen('wmic computersystem get TotalPhysicalMemory').read()
        lines = result.strip().splitlines()
        for line in lines:
            if line.strip().isdigit():
                total_memory_bytes = int(line.strip())
                return round(total_memory_bytes / (1024 ** 3), 2)

    def get_memory_size_linux(self):#테스트 필요
        """Linux에서 메모리 크기 가져오기"""
        with open('/proc/meminfo', 'r') as meminfo:
            for line in meminfo:
                if "MemTotal" in line:
                    parts = line.split()
                    if parts and parts[1].isdigit():
                        mem_kb = int(parts[1])
                        return round(mem_kb / (1024 ** 2), 2)

    def get_memory_size_macos(self):#테스트 필요
        """macOS에서 메모리 크기 가져오기"""
        result = os.popen('sysctl hw.memsize').read()
        parts = result.split(':')
        if len(parts) > 1:
            mem_bytes = int(parts[1].strip())
            return round(mem_bytes / (1024 ** 3), 2)

    def get_cpu_usage(self):
        """운영체제별 CPU 사용률 구하기"""
        system = platform.system()
        try:
            if system == "Windows":
                return self.get_cpu_usage_windows()
            elif system == "Linux":
                return self.get_cpu_usage_linux()
            elif system == "Darwin":
                return self.get_cpu_usage_macos()
        except Exception as e:
            print(f"Error fetching CPU usage: {e}")
            return "Error"

    def get_cpu_usage_windows(self):
        """Windows에서 CPU 사용률 가져오기"""
        result = os.popen("wmic cpu get loadpercentage").read().strip().splitlines()
        if len(result) >= 3:
            return int(result[2].strip())
            

    def get_cpu_usage_linux(self):#테스트 필요
        """Linux에서 CPU 사용률 가져오기"""
        result = os.popen("top -bn1 | grep 'Cpu(s)'").read()
        if result:
            idle = float(result.split('%id')[0].split()[-1])
            return round(100 - idle, 2)

    def get_cpu_usage_macos(self):#테스트 필요
        """macOS에서 CPU 사용률 가져오기"""
        result = os.popen("top -l 1 | grep 'CPU usage'").read()
        if result:
            user = float(result.split("user")[0].split()[-1])
            sys = float(result.split("sys")[0].split()[-1])
            return round(user + sys, 2)

    def get_memory_usage(self):
        """운영체제별 메모리 사용률 구하기"""
        system = platform.system()
        try:
            if system == "Windows":
                return self.get_memory_usage_windows()
            elif system == "Linux":
                return self.get_memory_usage_linux()
            elif system == "Darwin":
                return self.get_memory_usage_macos()
        except Exception as e:
            print(f"Error fetching memory usage: {e}")
            return "Error"

    def get_memory_usage_windows(self):
        """Windows에서 메모리 사용률 가져오기"""
        free = os.popen("wmic OS get FreePhysicalMemory").read().strip().splitlines()
        total = os.popen("wmic computersystem get TotalPhysicalMemory").read().strip().splitlines()
        if len(free) >= 3 and len(total) >= 3:
            free_memory = int(free[2].strip()) * 1024
            total_memory = int(total[2].strip())
            used_memory = total_memory - free_memory
            return round((used_memory / total_memory) * 100, 2)

    def get_memory_usage_linux(self):#테스트 필요
        """Linux에서 메모리 사용률 가져오기"""
        meminfo = os.popen("cat /proc/meminfo").read()
        lines = meminfo.splitlines()
        mem_total = int([x for x in lines if "MemTotal" in x][0].split()[1])
        mem_free = int([x for x in lines if "MemAvailable" in x][0].split()[1])
        used = mem_total - mem_free
        return round((used / mem_total) * 100, 2)

    def get_memory_usage_macos(self):#테스트 필요
        """macOS에서 메모리 사용률 가져오기"""
        total = int(os.popen("sysctl -n hw.memsize").read().strip())
        vm_stat = os.popen("vm_stat").read()
        page_size = 4096
        free_pages = 0
        for line in vm_stat.splitlines():
            if "Pages free" in line or "Pages inactive" in line:
                free_pages += int(line.split(":")[1].strip().replace('.', ''))
        free_memory = free_pages * page_size
        used_memory = total - free_memory
        return round((used_memory / total) * 100, 2)

    def print_json(self, data):
        """딕셔너리를 JSON 형식으로 출력"""
        json_str = "{\n"
        for key, value in data.items():
            if isinstance(value, str):
                value = f'"{value}"'
            elif value is None:
                value = "null"
            json_str += f'    "{key}": {value},\n'
        json_str = json_str.rstrip(',\n')
        json_str += "\n}"
        print(json_str)


if __name__ == '__main__':
    runComputer = MissionComputer()
    
    # 시스템 정보 출력
    system_info = runComputer.get_mission_computer_info()
    runComputer.print_json(system_info)
    
    # 시스템 부하 정보 출력
    load_info = runComputer.get_mission_computer_load()
    runComputer.print_json(load_info)