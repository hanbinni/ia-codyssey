text1 = 'Hello Mars'
print(text1)

file_path = 'mission_computer_main.log'

try:
    # 파일을 열어서 내용을 읽기
    file = open(file_path, 'r', encoding='utf-8')
    content = file.read()
    print(content)
    file.close()

except FileNotFoundError:
    print('파일이 존재하지 않습니다.')
except PermissionError:
    print('파일에 접근할 권한이 없습니다.')
except UnicodeDecodeError:
    print('파일 인코딩 오류.')
except MemoryError:
    print('메모리가 부족합니다.')
except OSError:
    print('파일을 열 수 없습니다.')
except Exception as e:
    print(f'알 수 없는 오류 발생: {e}')
