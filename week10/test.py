import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
import numpy as np

# ===== 설정 =====
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCK_DURATION = 0.5  # 0.5초마다 감지
SILENCE_TIMEOUT = 10  # 10초 이상 조용하면 저장
THRESHOLD = 0.02  # 음성 감지 임계값 (조절 가능)

# ===== 상태 변수 =====
recording = False
audio_buffer = []
last_sound_time = None

print("🎙️ 자비스 음성 감지 시스템 시작 (Ctrl+C로 종료)")

def callback(indata, frames, time, status):
    global recording, audio_buffer, last_sound_time

    volume_norm = np.linalg.norm(indata)  # RMS 계산

    if volume_norm > THRESHOLD:
        if not recording:
            print("🎤 음성 감지됨. 녹음 시작...")
            recording = True
            audio_buffer = []
        last_sound_time = datetime.now()
        audio_buffer.extend(indata.copy())
    elif recording:
        # 무음 감지 시간 체크
        if (datetime.now() - last_sound_time).total_seconds() > SILENCE_TIMEOUT:
            # 녹음 종료 및 저장
            filename = datetime.now().strftime("%Y%m%d-%H:%M:%S") + ".wav"
            filepath = "testrecords/" + filename
            write(filepath, SAMPLE_RATE, np.array(audio_buffer, dtype='int16'))
            print(f"💾 녹음 저장 완료: {filepath}")
            recording = False
            audio_buffer = []

try:
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS,
                        dtype='int16', blocksize=int(SAMPLE_RATE * BLOCK_DURATION),
                        callback=callback):
        while True:
            sd.sleep(100)  # 이벤트 루프 유지

except KeyboardInterrupt:
    print("\n🛑 시스템 종료됨.")
    if recording and audio_buffer:
        filename = datetime.now().strftime("%Y%m%d-%H:%M:%S") + ".wav"
        filepath = "testrecords/" + filename
        write(filepath, SAMPLE_RATE, np.array(audio_buffer, dtype='int16'))
        print(f"💾 마지막 녹음 저장: {filepath}")
