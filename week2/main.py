# Mission 3: Find the combustible substances

file_name = 'Mars_Base_Inventory_List.csv'  # 읽을 파일 경로로
binary_file_name = 'Mars_Base_Inventory_List.bin'  # 이진 파일 저장 경로
danger_file_name = 'Mars_Base_Inventory_danger.csv'  # CSV 파일 저장 경로
inventory_list = []  # 전체 데이터를 저장할 리스트
high_flammability_list = []  # 인화성 0.7 이상 데이터를 저장할 리스트



# 파일 저장 처리
def save_file(file_name, data_list, mode, encoding='utf-8'):
    try:
        if mode == 'csv':
            with open(file_name, 'w', encoding=encoding) as file:
                for item in data_list:
                    file.write(item + '\n') 
            print(f'\n✅ "{file_name}"로 저장되었습니다.')
        elif mode == 'binary':
            with open(file_name, 'wb') as file:  
                for item in data_list:
                    file.write(item.encode(encoding) + b'\n')  # UTF-8로 인코딩하여 저장
            print(f'\n✅ "{file_name}"로 이진 파일 저장되었습니다.')
    except IOError as e:
        print(f'❌ 파일 "{file_name}"을 저장하는 중 오류가 발생했습니다: {e}')
    except Exception as e:
        print(f'❌ 파일 저장 중 예기치 않은 오류 발생: {e}')


# 덮어쓰기 처리
def handle_file_existence(file_name, data_list, mode): #파일이 존재할 경우 덮어쓸지 물어보고 파일 저장
    try:
        with open(file_name, 'rb' if mode == 'binary' else 'r', encoding='utf-8' if mode == 'csv' else None):
            file_exists = True
    except FileNotFoundError:
        file_exists = False
        
    if file_exists and input(f'파일 "{file_name}"이 이미 존재합니다. 덮어쓰시겠습니까? (y/n): ').lower() != 'y':
        print(f'{file_name} 덮어쓰기를 취소합니다.') 
    else:
        save_file(file_name, data_list, mode)


# 이진 파일 읽기 및 내용 출력
def read_binary_file(file_name):
    try:
        with open(file_name, 'rb') as file:
            print(f'\n{file_name} 파일 내용:\n')
            for line in file:
                print(line.decode('utf-8').strip())  # 이진 데이터를 UTF-8로 디코딩하여 출력
    except FileNotFoundError:
        print(f'❌ 파일 "{file_name}"을 찾을 수 없습니다. 파일명이 올바른지 확인하세요.')
    except IOError as e:
        print(f'❌ 파일 "{file_name}"을 읽는 중 오류가 발생했습니다: {e}')
    except Exception as e:
        print(f'❌ 예기치 않은 오류 발생: {e}')


# main
try:
    # CSV 파일 읽기
    with open(file_name, 'r', encoding='utf-8') as file:
        header = file.readline().strip() # 헤더 분분리
        inventory_list.append(header)  # 리스트1에 헤더 추가
        high_flammability_list.append(header)  # 리스트2에도 헤더 추가

        data_rows = []  # 정렬을 위한 리스트
        for line in file:
            parts = line.strip().split(',')  # CSV 데이터 분리
            try:
                flammability = float(parts[4])  # 인화성 값을 숫자로 변환
                data_rows.append((flammability, line.strip()))  # (인화성, 데이터) 형태로 저장
            except ValueError:
                data_rows.append((0, line.strip()))  # 변환 불가능한 경우 0 처리

    # 1. 파일 내용 출력
    print('Mars_Base_Inventory_List.csv 파일 내용:\n')
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            print(line.strip())  # 공백 제거 후 처리

    # 2. 인화성 기준 내림차순 정렬 후 헤더와 병합
    data_rows.sort(reverse=True, key=lambda x: x[0])
    inventory_list.extend([row[1] for row in data_rows])

    # 4. 인화성 0.7 이상인 데이터만 필터링하여 저장
    high_flammability_list.extend([row[1] for row in data_rows if row[0] >= 0.7])

    # 5. 인화성 0.7 이상인 데이터 출력
    print('\n인화성이 0.7 이상인 데이터 리스트:\n')
    for item in high_flammability_list:
        print(item.strip())

    # 9. CSV 파일 저장 여부 확인 및 저장
    handle_file_existence(danger_file_name, high_flammability_list, 'csv')

    # 6. 이진 파일 저장 여부 확인 및 저장
    handle_file_existence(binary_file_name, inventory_list, 'binary')

    # 7. 이진 파일 읽기 및 출력
    read_binary_file(binary_file_name)

except FileNotFoundError:
    print(f'❌ 파일 "{file_name}"을 찾을 수 없습니다. 파일명이 올바른지 확인하세요.')
except PermissionError:
    print(f'❌ 파일 "{file_name}"에 대한 접근 권한이 없습니다. 권한 설정을 확인하세요.')
except UnicodeDecodeError:
    print(f'❌ 파일 "{file_name}"을 UTF-8 인코딩으로 읽을 수 없습니다. 다른 인코딩을 시도해 보세요.')
except IOError as e:
    print(f'❌ 파일 "{file_name}"을 읽는 중 입출력(IO) 오류가 발생했습니다: {e}')
except Exception as e:
    print(f'❌ 예기치 않은 오류 발생: {e}')
