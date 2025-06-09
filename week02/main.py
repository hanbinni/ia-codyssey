file_name = 'Mars_Base_Inventory_List.csv'  # 읽을 파일 경로
binary_file_name = 'Mars_Base_Inventory_List.bin'  # 이진 파일 저장 경로
danger_file_name = 'Mars_Base_Inventory_danger.csv'  # CSV 파일 저장 경로
inventory_list = []  # 전체 데이터를 저장할 리스트
high_flammability_list = []  # 인화성 0.7 이상 데이터를 저장할 리스트


# 파일 저장 처리
def save_file(file_name, data_list, mode):
    try:
        if mode == 'csv':
            with open(file_name, 'w', encoding='utf-8') as file:
                for item in data_list:
                    file.write(item + '\n')
            print(f'\n "{file_name}"로 저장되었습니다.')
        elif mode == 'binary':
            with open(file_name, 'wb') as file:
                for item in data_list:
                    binary_line = '|'.join(str(ord(char)) for char in item)  # ASCII 변환 후 '|'로 연결
                    file.write(binary_line.encode('utf-8') + b'\n')
            print(f'\n "{file_name}"로 이진 파일 저장되었습니다.')
    except IOError as e:
        print(f'파일 "{file_name}"을 저장하는 중 오류 발생: {e}')
    except Exception as e:
        print(f'예기치 않은 오류 발생: {e}')


# 덮어쓰기 처리
def handle_file_existence(file_name, data_list, mode):
    try:
        with open(file_name, 'rb' if mode == 'binary' else 'r', encoding='utf-8' if mode == 'csv' else None):
            file_exists = True
    except FileNotFoundError:
        file_exists = False

    if file_exists and input(f'파일 "{file_name}"이 이미 존재합니다. 덮어쓰시겠습니까? (y/n): ').lower() != 'y':
        print(f'{file_name} 덮어쓰기를 취소합니다.')
    else:
        save_file(file_name, data_list, mode)


# 이진 파일 읽기 및 출력
def read_binary_file(file_name):
    try:
        with open(file_name, 'rb') as file:
            print(f'\n{file_name} 파일 내용 (ASCII 복원):\n')
            for line in file:
                ascii_values = line.decode('utf-8').strip().split('|')
                restored_text = ''.join(chr(int(value)) for value in ascii_values)  # ASCII 값 → 문자 변환
                print(restored_text)
    except FileNotFoundError:
        print(f'파일 "{file_name}"을 찾을 수 없습니다.')
    except IOError as e:
        print(f'파일 "{file_name}"을 읽는 중 오류 발생: {e}')
    except Exception as e:
        print(f'예기치 않은 오류 발생: {e}')


# main
try:
    with open(file_name, 'r', encoding='utf-8') as file:
        header = file.readline().strip()
        inventory_list.append(header)
        high_flammability_list.append(header)

        data_rows = []
        for line in file:
            parts = line.strip().split(',')
            try:
                flammability = float(parts[4])
                data_rows.append((flammability, line.strip()))
            except ValueError:
                data_rows.append((0, line.strip()))

    # 파일 내용 출력
    print('Mars_Base_Inventory_List.csv 파일 내용:\n')
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            print(line.strip())

    # 인화성 기준 내림차순 정렬 후 병합
    data_rows.sort(reverse=True, key=lambda x: x[0])
    inventory_list.extend([row[1] for row in data_rows])

    # 인화성 0.7 이상 데이터 필터링
    high_flammability_list.extend([row[1] for row in data_rows if row[0] >= 0.7])

    # 인화성 0.7 이상 데이터 출력
    print('\n인화성이 0.7 이상인 데이터 리스트:\n')
    for item in high_flammability_list:
        print(item.strip())

    # CSV 파일 저장 여부 확인 및 저장
    handle_file_existence(danger_file_name, high_flammability_list, 'csv')

    # 이진 파일 저장 여부 확인 및 저장
    handle_file_existence(binary_file_name, inventory_list, 'binary')

    # 이진 파일 읽기 및 출력
    read_binary_file(binary_file_name)

except FileNotFoundError:
    print(f'파일 "{file_name}"을 찾을 수 없습니다.')
except PermissionError:
    print(f'파일 "{file_name}"에 대한 접근 권한이 없습니다.')
except UnicodeDecodeError:
    print(f'파일 "{file_name}"을 UTF-8 인코딩으로 읽을 수 없습니다.')
except IOError as e:
    print(f'파일 "{file_name}"을 읽는 중 입출력 오류 발생: {e}')
except Exception as e:
    print(f'예기치 않은 오류 발생: {e}')
