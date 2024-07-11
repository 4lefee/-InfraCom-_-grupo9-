import socket

class Node:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_node = None

    def send(self, data):
        self.socket.send(data.encode())

    def receive(self):
        return self.socket.recv(1024).decode()

    def listen(self):
        while True:
            try:
                data = self.receive()
                if data == "terminar":
                    break
                else:
                    print(f"Mensagem recebida: {data}")
            except OSError as e:
                print(f"Erro de socket: {e}")
                break

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    lista_ip_porta = [
        ("127.0.0.1", 8000),
        ("127.0.0.1", 8001),
        ("127.0.0.1", 8002),
        ("127.0.0.1", 8003),
        ("127.0.0.1", 8004)
    ]

    nós = [Node(ip, port) for ip, port in lista_ip_porta]
    for i, nó in enumerate(nós):
        nó.next_node = nós[(i + 1) % len(nós)]  
        print(f"Nó online: IP={nó.ip}, Porta={nó.port}, Próximo nó: IP={nó.next_node.ip}, Porta={nó.next_node.port}")


