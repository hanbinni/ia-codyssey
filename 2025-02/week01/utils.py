# utils.py
def broadcast(message, clients):
    for conn in list(clients.keys()):
        try:
            conn.send(message.encode())
        except:
            conn.close()
            del clients[conn]
