def generate_report(file_path):
    try:
        # 로그 파일 열기 (2번 줄부터 읽기)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()[1:]  # 첫 번째 줄을 제외하고 읽기

        # 이하 보고서서
        report = "# 미션 로그 분석 보고서\n\n"
        report += "## 로켓 발사 및 운영 로그\n\n"
        report += "|      Timestamp      | Event | Message |\n"
        report += "|---------------------|-------|---------|\n"

        for line in content:
            # ,기준 슬라이스스
            timestamp, event, message = line.strip().split(',', 2)
            report += f"|      {timestamp}      | {event} | {message} |\n"

        # 분석 내용
        report += "\n## 사고 분석\n\n"
        report += "### 산소 탱크 사고\n"
        report += "- **Timestamp**: 2023-08-27 11:35:00\n"
        report += "- **Description**: 산소 탱크는 11:35 AM에 불안정 상태로 보고되었고, 11:40 AM에 폭발했습니다. 이 사건은 미션에서 중요한 문제로 기록됩니다.\n"
        report += "- **Cause**: 산소 탱크의 불안정성은 제조 결함, 비정상적인 취급, 비행 중 고장 등 여러 원인으로 발생할 수 있습니다.\n"
        report += "- **Impact**: 산소 탱크의 폭발은 중요한 생명 유지 시스템의 손실을 초래했으며, 승무원과 미션 운영의 안전에 심각한 위협을 가했습니다.\n"
        report += "- **Recommended Action**: 산소 탱크의 설계, 설치 절차 및 취급 프로토콜을 철저히 조사하고, 미션 중 모든 시스템이 제대로 모니터링되고 테스트되도록 해야 합니다.\n"
        report += "\n### 요약\n"
        report += "- 미션은 11:35 AM까지 성공적으로 진행되었습니다. 그 시점까지 모든 시스템은 정상 작동했으며, 로켓은 발사, 궤도 진입, 착륙을 성공적으로 완료했습니다. 산소 탱크 문제는 로그에서 확인된 유일한 주요 실패 사항입니다.\n"

        # 파일 열기 시 덮어쓰기가 가능하게 기본적으로 파일을 열며
        # 예외 처리를 통해 덮어쓰기 여부 확인
        try:
            with open("log_analysis.md", "x", encoding="utf-8") as md_file:  # "x" 모드는 파일이 없으면 생성
                md_file.write(report)
            print("보고서가 성공적으로 생성되었습니다. 'log_analysis.md' 파일을 확인하세요.")
        except FileExistsError:
            user_input = input("'log_analysis.md' 파일이 이미 존재합니다. 덮어쓰시겠습니까? (y/n): ")
            if user_input.lower() == 'y':
                with open("log_analysis.md", "w", encoding="utf-8") as md_file:  # 덮어쓰기 모드로 열기
                    md_file.write(report)
                print("파일 덮어쓰기가 완료되었습니다.")
            else:
                print("파일 덮어쓰기를 취소했습니다.")
                
    except FileNotFoundError:
        print(f"오류: '{file_path}' 파일을 찾을 수 없습니다.")
    except PermissionError:
        print("파일에 접근할 권한이 없습니다.")
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")


# mission_computer_main.log 파일을 바탕으로 보고서를 생성합니다.
generate_report('mission_computer_main.log')
