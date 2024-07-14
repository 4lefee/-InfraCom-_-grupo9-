import os
import time
from create_nodes import Node
import socket


class FileTransferClient(Node):
    def __init__(self, ip, port):
        super().__init__(ip, port)

    def send_file(self, ip, port, file_path):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        file_size = os.path.getsize(file_path)
        client.send(f'PUTFILE {os.path.basename(file_path)} {file_size}'.encode())
        time.sleep(1)
        with open(file_path, 'rb') as file:
            client.sendall(file.read())
        client.close()
        print(f'Arquivo {file_path} enviado para {ip}:{port}')

    def receive_file(self, ip, port, file_name, save_path):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        client.send(f'GETFILE {file_name}'.encode())
        with open(save_path, 'wb') as file:
            while True:
                data = client.recv(1024)
                if not data:
                    break
                file.write(data)
        client.close()
        print(f'Arquivo {save_path} recebido de {ip}:{port}')

if __name__ == "__main__":
    cliente = FileTransferClient("127.0.0.1", 8001)
    destino_ip = "127.0.0.1"
    destino_port = 8000
    file_path = "upload/example_file.txt"
    save_path = "download/downloaded_example_file.txt"

    cliente.send_file(destino_ip, destino_port, file_path)
    time.sleep(2)

    cliente.receive_file(destino_ip, destino_port, os.path.basename(file_path), save_path)
