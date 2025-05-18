import time
from multiprocessing import Pool, cpu_count, Manager
from io import BytesIO
import zipfile

zip_filename = "ps.zip"
chars = "abcdefghijklmnopqrstuvwxyz0123456789"

# 4자리 문자열 조합 분배: 첫 글자별로 나누기
first_chars = [c for c in chars]

# ZIP 파일을 메모리에 올림
with open(zip_filename, "rb") as f:
    zip_data_global = f.read()

def try_password(zip_data, password):
    try:
        zip_mem = BytesIO(zip_data)
        with zipfile.ZipFile(zip_mem) as zf:
            zf.extractall(pwd=password.encode())
        return True
    except:
        return False

def worker(args):
    first_char, zip_data, found_flag = args

    if found_flag.value:
        return None  # 이미 찾았으면 종료

    print(f"[{first_char}***] 시도 시작")  # 진행상황 출력
    start_time = time.time()
    count = 0

    for c2 in chars:
        for c3 in chars:
            for c4 in chars:
                password = f"{first_char}{c2}{c3}{c4}"
                count += 1

                if try_password(zip_data, password):
                    with open("testpassword.txt", "w") as f:
                        f.write(password)
                    print(f"✅ 암호 해독 성공: {password}")
                    found_flag.value = True
                    return password

    elapsed = time.time() - start_time
    print(f"[{first_char}***] 시도 종료. 총 시도: {count}, 총 경과 시간: {elapsed:.2f}초")
    return None

def unlock_zip():
    num_processes = min(cpu_count(), len(first_chars))
    manager = Manager()
    found_flag = manager.Value('b', False)

    print("전체 작업 시작")
    start = time.time()

    with Pool(processes=num_processes) as pool:
        args_iterable = [(first_char, zip_data_global, found_flag) for first_char in first_chars]
        for result in pool.imap_unordered(worker, args_iterable, chunksize=1):
            if result is not None:
                break

    end = time.time()
    print(f"전체 작업 종료. 총 소요 시간: {end - start:.2f} 초")

if __name__ == "__main__":
    unlock_zip()
