
import smtplib  # SMTP 클라이언트 기능 제공(접속, 인증, 전송)




SENDER_EMAIL = "송신자 이메일" #gmail만 가능
SENDER_PASSWORD = "앱 비밀번호"
RECEIVER_EMAIL = "수신자 이메일"




def to_base64_manual(data: bytes) -> str:
    """
    역할: base64 모듈 없이 '직접' Base64 인코딩을 수행한다.
    파라미터:
      - data: 첨부파일 바이너리 데이터(bytes)
    동작 개요(Flow):
      1) 3바이트(24비트)씩 끊어서
      2) 6비트 단위로 4개 조각으로 나누고
      3) 인덱스 테이블(charset)로 문자 매핑
      4) 3바이트에 못 미치면 = 패딩을 붙인다.
    반환:
      - Base64로 인코딩된 문자열(str)
    """
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"  # 64문자 테이블
    result = ""     # 최종 Base64 문자열 누적 버퍼
    padding = ""    # 입력 길이가 3의 배수가 아닐 때 추가될 '=' 갯수 관리

    # [Flow-1] 입력 바이트를 3바이트씩 처리
    for i in range(0, len(data), 3):
        chunk = data[i:i+3]  # 현재 처리할 블록(최대 3바이트)

        # [Flow-1-1] 3바이트 미만이면 제로패딩(0x00)하고, 나중에 '=' 패딩 문자로 보정
        if len(chunk) < 3:
            padding = "=" * (3 - len(chunk))        # 부족한 바이트 수만큼 '=' 기록
            chunk += b"\x00" * (3 - len(chunk))     # 실제 비트 연산을 위해 0x00으로 채움

        # [Flow-1-2] 3바이트(24비트)를 정수로 합쳐서 6비트씩 4조각으로 분할
        n = (chunk[0] << 16) + (chunk[1] << 8) + chunk[2]

        # [Flow-1-3] 상위부터 6비트씩 잘라 charset 인덱싱 → Base64 문자 생성
        result += (
            charset[(n >> 18) & 63] +
            charset[(n >> 12) & 63] +
            charset[(n >> 6) & 63] +
            charset[n & 63]
        )

    # [Flow-2] 제로패딩으로 인해 생긴 마지막 문자들을 '='로 교체해 규약 준수
    if padding:
        result = result[:len(result) - len(padding)] + padding

    return result


def send_gmail(sender_email, sender_password, receiver_email, subject, body, attachment_path=None):
    """
    역할: Gmail SMTP 서버를 통해 메일 전송.
    파라미터:
      - sender_email     : 발신자 Gmail 주소 (앱 비밀번호 사용)
      - sender_password  : 발신자 '앱 비밀번호' (일반 비번 X)
      - receiver_email   : 수신자 이메일 주소
      - subject          : 메일 제목(평문, 한글 포함 가능. 단, 제목 인코딩은 생략하고 단순 문자열로 전송)
      - body             : 메일 본문(UTF-8 텍스트)
      - attachment_path  : 첨부파일 경로 (None이면 첨부 없이 일반 텍스트 메일 전송)
    흐름(Flow):
      1) SMTP 서버와 포트 설정
      2) 메일 헤더 작성 (From/To/Subject/MIME-Version)
      3) 첨부 여부에 따라 (a) multipart/mixed 또는 (b) text/plain으로 본문 조립
      4) 서버 연결 → TLS 시작 → 로그인 → 메일 전송
      5) 예외 처리
    """
    # [Var] SMTP 서버 접속 정보
    smtp_server = "smtp.gmail.com"  # Gmail SMTP 호스트
    smtp_port = 587                 # STARTTLS(암호화 전환)용 표준 포트

    # [Var] 멀티파트 경계 문자열 (본문과 첨부파일 파트를 구분)
    #      고유 문자열이면 충분하며, 충돌 위험이 낮은 문자열로 구성
    boundary = "----=_Boundary1234567890"

    # [Flow-1] 공통 메일 헤더 작성
    #  - MIME-Version: MIME 사용 선언 (멀티파트/텍스트 모두에 적절)
    #  - Subject: 여기서는 인코딩 없이 평문 사용(간단화). 한글 완전 호환성 필요 시 RFC2047 인코딩 권장.
    headers = f"""From: {sender_email}
To: {receiver_email}
Subject: {subject}
MIME-Version: 1.0
"""

    # [Flow-2] 첨부 여부에 따른 본문 조립
    if attachment_path:
        # [Var] 파일명 추출: os.path.basename 없이 경로 구분자 기준 수동 분리
        filename = attachment_path.split("/")[-1] if "/" in attachment_path else attachment_path.split("\\")[-1]

        # [Flow-2-1] 파일을 바이너리 읽기
        with open(attachment_path, "rb") as f:
            file_data = f.read()

        # [Flow-2-2] 첨부파일을 수동 Base64 인코딩(ASCII-safe 전송을 위해 필수)
        encoded_file = to_base64_manual(file_data)

        # [Flow-2-3] multipart/mixed 메시지 구성
        #  - 첫 파트: text/plain; charset=UTF-8  → 본문
        #  - 둘째 파트: application/octet-stream; base64 → 첨부파일
        message = (
            headers
            + f'Content-Type: multipart/mixed; boundary="{boundary}"\n\n'
            # -- 본문 파트 시작 --
            + f'--{boundary}\n'
            + 'Content-Type: text/plain; charset="UTF-8"\n\n'
            + f'{body}\n\n'
            # -- 첨부파일 파트 시작 --
            + f'--{boundary}\n'
            + f'Content-Type: application/octet-stream; name="{filename}"\n'
            + 'Content-Transfer-Encoding: base64\n'
            + f'Content-Disposition: attachment; filename="{filename}"\n\n'
            + f'{encoded_file}\n'
            # -- 멀티파트 종료 --
            + f'--{boundary}--'
        )
    else:
        # [Flow-2-Alt] 첨부가 없으면 단순 text/plain 본문만 구성
        message = (
            headers
            + 'Content-Type: text/plain; charset="UTF-8"\n\n'
            + body
        )

    # [Flow-3] SMTP 연결/인증/전송 + 예외 처리
    try:
        # [Step-1] 서버 연결(평문 채널)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # [Step-2] 서버 인사(EHLO) → 기능 협상
            server.ehlo()

            # [Step-3] STARTTLS로 보안(암호화) 채널 전환
            server.starttls()

            # [Step-4] 암호화 전환 이후 EHLO 재호출(권장)
            server.ehlo()

            # [Step-5] 로그인 (앱 비밀번호 필수)
            server.login(sender_email, sender_password)

            # [Step-6] 메일 전송 (바이트로 전송. UTF-8 인코딩)
            server.sendmail(sender_email, receiver_email, message.encode("utf-8"))

            # [Step-7] 사용자 피드백
            print("✅ 메일 전송 완료!")

    # [예외 처리] 파일/인증/연결/수신자/데이터/네트워크/기타
    except FileNotFoundError:
        # 첨부파일 경로 오류
        print(f"❌ 첨부파일 '{attachment_path}'을(를) 찾을 수 없습니다.")
    except smtplib.SMTPAuthenticationError:
        # 계정/앱 비밀번호 문제
        print("❌ 로그인 실패: Gmail 계정 또는 앱 비밀번호를 확인하세요.")
    except smtplib.SMTPConnectError:
        # SMTP 서버 연결 실패
        print("❌ SMTP 서버에 연결할 수 없습니다.")
    except smtplib.SMTPRecipientsRefused:
        # 수신자 주소 거부(존재하지 않는 주소 등)
        print("❌ 수신자 이메일 주소가 거부되었습니다.")
    except smtplib.SMTPDataError as e:
        # DATA 단계 전송 오류(정책 위반, 용량 초과 등)
        print(f"❌ 데이터 전송 오류: {e}")
    except ConnectionError:
        # 광범위한 네트워크 연결 문제(소켓 모듈 없이 포괄 처리)
        print("❌ 네트워크 연결에 문제가 있습니다. 인터넷 연결을 확인하세요.")
    except OSError as e:
        # 시스템 수준(파일/네트워크)의 일반적 오류 포괄 처리
        print(f"⚠️ 시스템 수준 오류: {e}")
    except Exception as e:
        # 모든 예기치 못한 상황
        print(f"⚠️ 예기치 못한 오류 발생: {e}")


# ===== 실행 예시 =====
if __name__ == "__main__":

    subject = "SMTP 메일 테스트"           # 메일 제목(간단화: 평문)
    body = "이 메일은 테스트 메일입니다."  # 본문(UTF-8)
    attachment_path = "example.txt"        # 첨부 경로 (없으면 None)

    # [Flow] 전송 호출
    send_gmail(SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL, subject, body, attachment_path)
