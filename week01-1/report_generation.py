def read_log_file(file_path):
    log_list = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()[1:]  # 첫 번째 줄 제외
            
            for line in content:
                parts = line.strip().split(',', 2)
                if len(parts) == 3:
                    timestamp, event, message = parts
                    log_list.append([timestamp, event, message])
                
        return log_list
    except FileNotFoundError:
        print(f'오류: "{file_path}" 파일을 찾을 수 없습니다.')
        return []
    except Exception as e:
        print(f'알 수 없는 오류 발생: {e}')
        return []

def convert_list_to_dict(log_list):
    log_dict = {}
    
    for log in log_list:
        timestamp, event, message = log
        log_dict[timestamp] = {'event': event, 'message': message}
    
    return log_dict

def save_dict_to_json(log_dict, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json_content = '{\n'
            json_content += ',\n'.join(f'    "{timestamp}": {{ "event": "{details['event']}", "message": "{details['message']}" }}' for timestamp, details in log_dict.items())
            json_content += '\n}'
            json_file.write(json_content)
        print(f'JSON 파일이 생성되었습니다: {output_file}')
    except Exception as e:
        print(f'JSON 파일 저장 중 오류 발생: {e}')

def search_log(log_dict):
    while True:
        keyword = input('\n검색할 키워드를 입력하세요 ("exit" 입력 시 종료): ')
        if keyword.lower() == 'exit':
            print('프로그램을 종료합니다.')
            break
        
        keyword_lower = keyword.lower()
        results = {timestamp: details for timestamp, details in log_dict.items() 
                   if keyword_lower in details['event'].lower() or keyword_lower in details['message'].lower()}
        
        if results:
            print('\n검색 결과:')
            for timestamp, details in results.items():
                print(f'{timestamp}: {details}')
        else:
            print('\n검색 결과가 없습니다.')

def main():
    file_path = 'mission_computer_main.log'
    output_file = 'mission_computer_main.json'
    
    logs = read_log_file(file_path)
    
    if logs:
        logs.sort(reverse=True, key=lambda x: x[0])  # 시간의 역순 정렬
        print('시간 역순으로 정렬된 리스트 객체:')
        for log in logs:
            print(log)
        
        log_dict = convert_list_to_dict(logs)
        print('\n사전(Dict) 객체로 변환된 데이터:')
        print(log_dict)
        
        save_dict_to_json(log_dict, output_file)
        
        search_log(log_dict)

if __name__ == '__main__':
    main()
