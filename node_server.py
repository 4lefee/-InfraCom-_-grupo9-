import socket
import time
from create_nodes import Node

def run_server(nó):
        nó.socket.bind((nó.ip, nó.port))
        nó.socket.listen() 
        print(f"Nó {nó.ip}:{nó.port} aguardando conexão...")
        connection, address = nó.socket.accept()
        print(f"Conexão aceita de {address}")

        while True:
            data = connection.recv(1024).decode()
            if not data:
                break
            print(f"Mensagem recebida: {data}")
            if data == "terminar":
                nó.socket.close()
                break
                

if __name__ == "__main__":
    nó_servidor = Node("127.0.0.1", 8000)

    run_server(nó_servidor)
