# handler.py
from utils import broadcast

def client_handler(conn, addr, clients):
    nickname = conn.recv(1024).decode()
    clients[conn] = nickname
    broadcast(f"📢 {nickname}님이 입장하셨습니다.", clients)

    while True:
        try:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            if msg == "/종료":
                conn.close()
                del clients[conn]
                broadcast(f"❌ {nickname}님이 퇴장하셨습니다.", clients)
                break
            else:
                broadcast(f"{nickname}> {msg}", clients)
        except:
            conn.close()
            if conn in clients:
                del clients[conn]
            break
