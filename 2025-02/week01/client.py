# client.py
import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

def receive_messages(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if not msg:
                break
            print(msg)
        except:
            break

def main():
    nickname = input("사용자 이름 입력: ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(nickname.encode())

    threading.Thread(target=receive_messages, args=(client,)).start()

    while True:
        msg = input()
        if msg == "/종료":
            client.send("/종료".encode())
            client.close()
            break
        else:
            client.send(msg.encode())

if __name__ == "__main__":
    main()
