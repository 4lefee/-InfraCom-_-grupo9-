import socket
import time
from create_nodes import Node

def run_client(nó, nó_destino):
    nó.socket.connect((nó_destino.ip, nó_destino.port))
    print(f"Nó {nó.ip}:{nó.port} conectado a {nó_destino.ip}:{nó_destino.port}")

    time.sleep(2)

    nó.send('olá')

    print(f"Mensagem recebida: {nó.receive()}")

    nó.socket.close()

if __name__ == "__main__":
    nó_cliente = Node("127.0.0.1", 8001)

    nó_destino = Node("127.0.0.1", 8000)

    run_client(nó_cliente, nó_destino)
