# server.py
import socket
import threading
from handler import client_handler
from utils import broadcast

HOST = '127.0.0.1'
PORT = 5000

clients = {}  # {conn: nickname}

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"서버 시작됨 {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        print(f"{addr} 연결됨")
        threading.Thread(target=client_handler, args=(conn, addr, clients)).start()

if __name__ == "__main__":
    main()
