import sounddevice as sd
import wave
from datetime import datetime
import os

# ====== 전역 설정 ======
SAMPLE_RATE = 44100
CHANNELS = 1
RECORD_DIR = 'records'
audio_buffer = bytearray()


# ====== 유틸리티 함수 ======

def ensure_record_dir():
    """녹음 파일 저장 디렉터리가 없으면 생성."""
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)


def get_valid_date(prompt):
    """날짜 입력을 받아 유효한 datetime 객체로 반환."""
    while True:
        date_input = input(prompt).strip()
        try:
            return datetime.strptime(date_input, '%Y%m%d')
        except ValueError:
            print("❌ 올바른 날짜 형식이 아닙니다. (예: 20250601)")


# ====== 녹음 관련 ======

def callback(indata, frames, time, status):
    """녹음 콜백 함수: 입력된 데이터를 전역 버퍼에 저장."""
    global audio_buffer
    audio_buffer.extend(indata.tobytes())


def save_recording():
    """녹음 데이터를 .wav 파일로 저장."""
    if not audio_buffer:
        return

    filename = datetime.now().strftime('%Y%m%d-%H:%M:%S') + '.wav'
    filepath = os.path.join(RECORD_DIR, filename)

    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio_buffer)

    print(f"\n💾 저장 완료: {filepath}")


def start_recording():
    """실제 녹음을 시작하고, Ctrl+C로 종료 시 저장."""
    global audio_buffer
    audio_buffer = bytearray()
    print("🎤 녹음 중입니다. 종료하려면 Ctrl+C를 입력하세요.")

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', callback=callback):
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\n🛑 녹음 종료됨.")
        save_recording()


# ====== 리스트 관련 ======

def list_recordings_by_date():
    """사용자로부터 날짜 범위를 입력받고, 해당 날짜 범위의 녹음 파일을 출력."""
    ensure_record_dir()
    start = get_valid_date("🗓️ 시작 날짜 입력 (예: 20250601): ")

    while True:
        end = get_valid_date("🗓️ 종료 날짜 입력 (예: 20250603): ")
        if end < start:
            print("❌ 종료 날짜는 시작 날짜 이후여야 합니다.")
        else:
            break

    files = [f for f in os.listdir(RECORD_DIR) if f.endswith('.wav')]

    print(f"\n📁 {start.strftime('%Y%m%d')} ~ {end.strftime('%Y%m%d')} 범위의 녹음 파일:")
    found = False
    for file in sorted(files):
        try:
            date_str = file.split('-')[0]
            file_date = datetime.strptime(date_str, '%Y%m%d')
            if start <= file_date <= end:
                print('🔹', file)
                found = True
        except Exception:
            continue

    if not found:
        print("📭 해당 범위의 파일이 없습니다.")


# ====== 메인 프로그램 ======

def main_menu():
    """사용자에게 메뉴 선택을 받아 각 기능으로 분기."""
    while True:
        print("\n🎛 자비스 시스템")
        print("녹음 시작(1) / 녹음 리스트 보기(2) / 시스템 종료(q)")
        choice = input("번호 선택 : ").strip()

        if choice == '1':
            start_recording()
            break  # 녹음 후 시스템 종료
        elif choice == '2':
            list_recordings_by_date()
        elif choice == 'q':
            print("👋 시스템을 종료합니다.")
            break
        else:
            print("❌ 잘못된 입력입니다. 1, 2 또는 q를 입력하세요.")


if __name__ == '__main__':
    ensure_record_dir()
    main_menu()
