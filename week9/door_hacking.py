import time
from multiprocessing import Pool, cpu_count, Manager
from io import BytesIO
import zipfile

zip_filename = "emergency_storage_key.zip"
chars = "abcdefghijklmnopqrstuvwxyz0123456789"
first_two_chars = [a + b for a in chars for b in chars]

# ZIP 파일을 메모리에 올림
with open(zip_filename, "rb") as f:
    zip_data_global = f.read()  # 전역 zip 데이터

def try_password(zip_data, password):
    try:
        zip_mem = BytesIO(zip_data)
        with zipfile.ZipFile(zip_mem) as zf:
            zf.extractall(pwd=password.encode())
        return True
    except:
        return False

def worker(args):
    first_two, zip_data, found_flag = args

    if found_flag.value:
        return None  # 시작 전에 확인하고 종료

    print(f"[{first_two}***] 시도 시작")
    start_time = time.time()
    count = 0

    for c3 in chars:
        print(f"[{first_two}{c3}***] 시도 중...")
        for c4 in chars:
            for c5 in chars:
                for c6 in chars:
                    password = f"{first_two}{c3}{c4}{c5}{c6}"
                    count += 1
                    if try_password(zip_data, password):
                        with open("password.txt", "w") as f:
                            f.write(password)
                        print(f"✅ 암호 해독 성공: {password}")
                        found_flag.value = True
                        elapsed = time.time() - start_time
                        print(f"[{first_two}***] 시도 종료. 총 시도: {count}, 총 경과 시간: {elapsed:.2f}초")
                        return password

    elapsed = time.time() - start_time
    print(f"[{first_two}***] 시도 종료. 총 시도: {count}, 총 경과 시간: {elapsed:.2f}초")
    return None

def unlock_zip():
    num_processes = cpu_count()
    manager = Manager()
    found_flag = manager.Value('b', False)

    start = time.time()
    with Pool(processes=num_processes) as pool:
        args_iterable = [(first_two, zip_data_global, found_flag) for first_two in first_two_chars]
        for result in pool.imap_unordered(worker, args_iterable, chunksize=27):
            if result is not None:
                break
    end = time.time()
    print(f"총 시도 시간: {end - start:.2f} 초")

if __name__ == "__main__":
    unlock_zip()
