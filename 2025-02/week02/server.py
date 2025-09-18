from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
# 추가문제
import urllib.request
import json


class PirateHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """클라이언트의 GET 요청 처리"""

        # favicon.ico 요청 무시
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        client_ip = self.get_client_ip()
        location_info = self.get_location_info(client_ip)

        # index.html 읽기
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            self.send_error(404, "File Not Found")
            return

        # index.html + 접속 정보 추가
        content += f"""
        <hr>
        <h3>당신의 접속 정보</h3>
        <p><strong>IP 주소:</strong> {client_ip}</p>
        <p><strong>위치 정보:</strong> {location_info or '확인 불가'}</p>
        """

        # 200 OK 응답
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        self.wfile.write(content.encode("utf-8"))

        # 서버 콘솔 로그
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] 클라이언트 접속 - IP: {client_ip}, 위치: {location_info}")

    def get_client_ip(self):
        """
        클라이언트 IP 판별:
        - X-Forwarded-For: ngrok, 로드밸런서, 프록시 환경에서 실제 클라이언트 IP
        - self.client_address[0]: 직접 연결된 경우 (로컬/서버에 바로 접속한 경우)
        """
        forwarded_for = self.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return self.client_address[0]

    def get_location_info(self, ip):
        """
        ipinfo.io API로 위치 정보 조회
        - 사설망(127.x, 192.168.x, 10.x)은 조회 안 함
        - 결과 예시: 'KR Seoul Seoul / AS12345 SomeISP'
        """
        if ip.startswith(("127.", "192.168.", "10.")):
            return None
        try:
            url = f"https://ipinfo.io/{ip}/json"
            with urllib.request.urlopen(url) as response:
                data = response.read()
                result = json.loads(data.decode("utf-8"))
                country = result.get("country", "알 수 없음")
                region = result.get("region", "")
                city = result.get("city", "")
                org = result.get("org", "")
                return f"{country} {region} {city} / {org}".strip()
        except Exception as e:
            print(f"위치 조회 오류: {e}")
        return None


def run_server():
    host = ("", 8080)
    httpd = HTTPServer(host, PirateHandler)
    print("서버 시작: http://localhost:8080")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n서버 종료")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
