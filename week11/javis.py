# 10주차 라이브러리
import os  # 목록 열람, 경로 조합
import wave  # 녹음 파일 저장
import sounddevice as sd  # 음성 녹음
from datetime import datetime  # 날짜 처리
# stt 처리 부분
import whisper  # STT 처리
from pydub import AudioSegment  # 전처리 (사용 안함)

# STT처리
device = "cpu"
MODEL_NAME = "base"
model = whisper.load_model(MODEL_NAME, device=device)

# 경로
RECORD_DIR = '../week10/records'
OUTPUT_DIR = 'csvdir'

# 녹음 처리
SAMPLE_RATE = 44100
CHANNELS = 1
audio_buffer = bytearray()

# ====== STT 처리 함수 ======

def preprocess_audio(file_path):
    """
    Whisper 모델용으로 오디오 전처리 (모노 + 16kHz + 정규화)
    - tempfile 없이 고정된 경로에 저장
    """
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)

    gain = 0 if audio.dBFS == float("-inf") else -audio.dBFS
    audio = audio.apply_gain(gain)

    # 원래 파일 이름 기준으로 새로운 파일명 생성
    base, _ = os.path.splitext(file_path)
    processed_path = base + "_processed.wav"
    audio.export(processed_path, format="wav")

    return processed_path


def transcribe_audio(file_path):
    """Whisper STT 수행 (언어: 한국어)"""
    result = model.transcribe(file_path, language="ko")
    segments = result.get("segments", [])
    return [
        {
            "time": f"{round(seg['start'], 2)}s",
            "text": seg['text'].strip()
        }
        for seg in segments
    ]


def run_stt_on_files():
    """녹음 파일 목록 확인 후 사용자 승인 받아 STT를 수행하고 CSV로 저장"""
    if not os.path.exists(RECORD_DIR):
        print("❌ 입력 폴더가 존재하지 않습니다:", RECORD_DIR)
        return

    files = [f for f in os.listdir(RECORD_DIR) if f.endswith((".mp3", ".wav", ".m4a"))]
    if not files:
        print("📭 변환할 음성 파일이 없습니다.")
        return

    # 파일 목록 출력
    print("\n📁 변환 가능한 녹음 파일 목록:")
    for idx, filename in enumerate(sorted(files), start=1):
        print(f"{idx:2d}. {filename}")

    # 사용자 확인
    confirm = input("\n📝 위 파일들에 대해 STT 변환을 진행할까요? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❎ STT 변환이 취소되었습니다.")
        return

    # 출력 폴더 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # STT 수행 및 CSV 저장
    for filename in files:
        print(f"🎙 처리 중: {filename}")
        input_path = os.path.join(RECORD_DIR, filename)

        transcription = transcribe_audio(input_path)

        base_name = os.path.splitext(filename)[0]
        csv_path = os.path.join(OUTPUT_DIR, base_name + ".csv")

        # pandas 없이 CSV 파일 저장
        with open(csv_path, 'w', encoding='utf-8-sig') as f:
            f.write("time,text\n")
            for row in transcription:
                f.write(f"{row['time']},{row['text']}\n")

        print(f"✅ 저장 완료: {csv_path}")


# 10주차 작성 부분

def ensure_record_dir():
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)

def get_valid_date(prompt):
    while True:
        date_input = input(prompt).strip()
        try:
            return datetime.strptime(date_input, '%Y%m%d')
        except ValueError:
            print("❌ 올바른 날짜 형식이 아닙니다. (예: 20250601)")

def callback(indata, frames, time, status):
    global audio_buffer
    audio_buffer.extend(indata.tobytes())

def save_recording():
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

def list_recordings_by_date():
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


# ====== 메인 메뉴 ======

def main_menu():
    while True:
        print("\n🎛 자비스 시스템")
        print("1️⃣ 녹음 시작")
        print("2️⃣ 녹음 리스트 보기")
        print("3️⃣ STT 변환 실행 ")
        print("q️⃣ 시스템 종료")
        choice = input("번호 선택 : ").strip()

        if choice == '1':
            start_recording()
            break
        elif choice == '2':
            list_recordings_by_date()
        elif choice == '3':
            run_stt_on_files()
        elif choice == 'q':
            print("👋 시스템을 종료합니다.")
            break
        else:
            print("❌ 잘못된 입력입니다. 1, 2, 3 또는 q를 입력하세요.")


# ====== 실행 진입점 ======
if __name__ == '__main__':
    ensure_record_dir()
    main_menu()
