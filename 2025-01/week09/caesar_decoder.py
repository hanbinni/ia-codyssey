# ====================== 파일 설정 ======================

ENCRYPTED_FILE = 'password.txt'
DICTIONARY_FILE = 'dictionary.txt'
RESULT_FILE = 'result.txt'


# ====================== 화면 관련 유틸리티 ======================

# 터미널 클리어
def clear_screen():
    print("\033c", end='')


# ====================== 암호 관련 기능 ======================

# 복호화 알고리즘
def decode_with_key(text, key, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    return ''.join(
        alphabet[(alphabet.index(c) - key) % 26] if c in alphabet else c
        for c in text
    )

# 해독 문자열 생성
def get_cipher_table_string(alphabet, key):
    cipher_line = '암호 알파벳 : ' + ' '.join(alphabet)
    plain_line = '해독 알파벳 : ' + ' '.join(
        alphabet[(alphabet.index(ch) - key) % 26] for ch in alphabet
    )
    return f"{cipher_line}\n{plain_line}"


# ====================== 파일 입출력 기능 ======================

# 암호파일 로드
def read_encrypted_text(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"암호문 파일 '{file_path}'을(를) 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"암호문 파일 읽기 오류: {e}")
        return None

# 사전 로드
def load_dictionary(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            words = [w.strip().upper()
                     for line in f
                     for w in line.replace(',', ' ').split()
                     if w.strip()]
            return words
    except FileNotFoundError:
        print(f"사전 파일 '{file_path}'을(를) 찾을 수 없습니다. 단어 검색 기능은 비활성화됩니다.")
        return []
    except Exception as e:
        print(f"사전 파일 읽기 오류: {e}")
        return []

# 결과 출력
def save_decoded_result(filename, decoded_text, key, original_text, alphabet):
    try:
        cipher_table = get_cipher_table_string(alphabet, key)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=== 시저 암호 해독 결과 ===\n")
            f.write(f"사용한 키 : {key}\n\n")
            f.write(f"[원본 암호문]\n{original_text}\n\n")
            f.write(f"[해독된 평문]\n{decoded_text}\n\n")
            f.write(f"[암호표 (Cipher Table)]\n{cipher_table}\n")

        print(f"\n키 {key}로 해독한 결과를 '{filename}'에 저장했습니다.")
    except Exception as e:
        print(f"결과 저장 오류: {e}")


# ====================== 사용자 입력 처리 ======================

# 입력 문자열 처리
def get_user_input(prompt):
    return input(prompt).strip().lower()


# ====================== 디코딩 로직 ======================

# 사전 참조
def check_dictionary_words(decoded_text, dictionary_words):
    return [w for w in dictionary_words if w in decoded_text]

# 암호표
def print_cipher_table(alphabet, key):
    print(f"암호표 (키 = {key} 기준)")
    print("-" * 50)
    print(get_cipher_table_string(alphabet, key))
    print("-" * 50 + "\n")

# 실제 터미널 출력 메서드
def show_decoding_result(key, original_text, decoded_text, alphabet):
    clear_screen()
    print("=" * 60)
    print(f"원본 암호문 : {original_text}")
    print("=" * 60)
    print("알파벳 기준 : A ~ Z (대문자)")
    print_cipher_table(alphabet, key)
    print(f"키 {key} 해독 결과 : {decoded_text}")
    print("=" * 60)


# ====================== 해독 루프 ======================

# 실제 암호 해독 루프
def caesar_cipher_decode(target_text, dictionary_words):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    text_upper = target_text.upper()
    key = 1

    while True:
        decoded = decode_with_key(text_upper, key, alphabet)
        show_decoding_result(key, text_upper, decoded, alphabet)

        found = check_dictionary_words(decoded, dictionary_words)
        if found:
            print(f"!! 사전 단어 발견: {', '.join(found)}")
            proceed = find_dictionary_words(target_text=decoded, key=key, original_text=text_upper, alphabet=alphabet)
            if not proceed:
                break
            else:
                key = key + 1 if key < 26 else key
        else:
            cmd = get_user_input("y=맞음, n=다음, b=이전, 숫자(1~26)=이동, q=종료 : ")

            if cmd == 'y':
                save_decoded_result(RESULT_FILE, decoded, key, text_upper, alphabet)
                break
            elif cmd == 'n':
                key = key + 1 if key < 26 else key
            elif cmd == 'b':
                key = key - 1 if key > 1 else key
            elif cmd.isdigit():
                num = int(cmd)
                if 1 <= num <= 26:
                    key = num
                else:
                    print("1~26 사이 숫자만 입력하세요.")
                    input("계속하려면 Enter를 누르세요...")
            elif cmd == 'c':
                key = key + 1 if key < 26 else key
            elif cmd == 'q':
                print("프로그램을 종료합니다.")
                break
            else:
                print("잘못된 입력입니다.")
                input("계속하려면 Enter를 누르세요...")

# 사전에 단어 있는 경우 처리
def find_dictionary_words(target_text, key, original_text, alphabet):
    user_input = get_user_input("계속 진행하시겠습니까? (s=중지 저장, c=계속) ")

    if user_input == 's':
        save_decoded_result(RESULT_FILE, target_text, key, original_text, alphabet)
        return False  # 중지
    elif user_input == 'c':
        return True  # 계속 진행
    else:
        print("잘못된 입력입니다. 계속 진행합니다.")
        input("계속하려면 Enter를 누르세요...")
        return True  # 계속 진행


# ====================== 프로그램 진입점 ======================

def main():
    encrypted = read_encrypted_text(ENCRYPTED_FILE) # 암호문
    if encrypted is None:
        return
    dictionary = load_dictionary(DICTIONARY_FILE) # 사전
    caesar_cipher_decode(encrypted, dictionary) # 해독 처리


if __name__ == '__main__':
    main()
