import smtplib
import csv
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# =========================
# 🔹 설정값
# =========================
SENDER_EMAIL = "송신자 이메일"      # Gmail 또는 Naver 둘 다 가능
SENDER_PASSWORD = "앱 비밀번호"
CSV_FILE = "mail_target_list.csv"
HTML_TEMPLATE_FILE = "template.html"

# =========================
# 🔹 HTML 템플릿 로드
# =========================
def load_html_template(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ HTML 템플릿 파일 '{filepath}'을(를) 찾을 수 없습니다.")
        return None

# =========================
# 🔹 SMTP 분기 선택 함수
# =========================
def select_smtp_server(sender_email: str):
    sender_email = sender_email.lower()

    if "@gmail.com" in sender_email:
        return {
            "server": "smtp.gmail.com",
            "port": 587,
            "use_ssl": False,
            "description": "Gmail SMTP (앱 비밀번호 필요)"
        }
    elif "@naver.com" in sender_email:
        return {
            "server": "smtp.naver.com",
            "port": 465,
            "use_ssl": True,
            "description": "Naver SMTP (IMAP/SMTP 사용함 설정 필요)"
        }
    else:
        raise ValueError("지원하지 않는 메일 도메인입니다. Gmail 또는 Naver만 가능합니다.")

# =========================
# 🔹 HTML 메일 발송
# =========================
def send_html_email(sender_email, sender_password, receiver_email, receiver_name, subject, html_body):
    smtp_info = select_smtp_server(sender_email)
    smtp_server = smtp_info["server"]
    smtp_port = smtp_info["port"]

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if smtp_info["use_ssl"]:
            # ✅ Naver용 SSL 연결
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
        else:
            # ✅ Gmail용 STARTTLS 연결
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())

        print(f"✅ {receiver_name}({receiver_email})에게 메일 전송 완료! ({smtp_info['description']})")

    except smtplib.SMTPAuthenticationError:
        print("❌ 로그인 실패: 비밀번호나 SMTP 설정을 확인하세요.")
    except Exception as e:
        print(f"⚠️ {receiver_name}({receiver_email}) 메일 전송 중 오류: {e}")

# =========================
# 🔹 CSV 읽기
# =========================
def read_csv_targets(csv_path):
    targets = []
    try:
        with open(csv_path, newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # 헤더 스킵
            for row in reader:
                if len(row) >= 2:
                    name, email = row[0].strip(), row[1].strip()
                    if email:
                        targets.append((name, email))
    except FileNotFoundError:
        print(f"❌ '{csv_path}' 파일을 찾을 수 없습니다.")
    return targets

# =========================
# 🔹 메인 실행
# =========================
if __name__ == "__main__":
    subject = "📢 SMTP 자동 분기 테스트 메일"
    html_template = load_html_template(HTML_TEMPLATE_FILE)
    if not html_template:
        exit()

    targets = read_csv_targets(CSV_FILE)
    print(f"📋 총 {len(targets)}명에게 메일 전송 시작...\n")

    for name, email in targets:
        html_body = html_template.format(name=name)
        send_html_email(SENDER_EMAIL, SENDER_PASSWORD, email, name, subject, html_body)

    print("\n✅ 전체 메일 발송 완료!")
