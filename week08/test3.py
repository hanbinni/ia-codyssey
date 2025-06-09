import time
import zipfile

zip_filename = "emergency_storage_key.zip"
chars = "abcdefghijklmnopqrstuvwxyz0123456789"
first_two_chars = [a + b for a in chars for b in chars]

def try_password(zip_filename, password):
    try:
        with zipfile.ZipFile(zip_filename) as zf:
            zf.extractall(pwd=password.encode())
        return True
    except:
        return False

def unlock_zip():
    start_time = time.time()
    for first_two in first_two_chars:
        print(f"[{first_two}***] 시도 시작")
        count = 0
        for c3 in chars:
            print(f"[{first_two}{c3}***] 시도 중...")
            for c4 in chars:
                for c5 in chars:
                    for c6 in chars:
                        password = f"{first_two}{c3}{c4}{c5}{c6}"
                        count += 1
                        if try_password(zip_filename, password):
                            elapsed = time.time() - start_time
                            print(f"✅ 암호 해독 성공: {password}")
                            print(f"[{first_two}***] 시도 종료. 총 시도: {count}, 총 경과 시간: {elapsed:.2f}초")
                            return
        elapsed = time.time() - start_time
        print(f"[{first_two}***] 시도 종료. 총 시도: {count}, 경과 시간: {elapsed:.2f}초")
    print("암호를 찾지 못했습니다.")

if __name__ == "__main__":
    unlock_zip()
