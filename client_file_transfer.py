# file_transfer.py
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
    lista_ip_porta = [
        ("127.0.0.1", 8000),
        ("127.0.0.1", 8001),
        ("127.0.0.1", 8002),
        ("127.0.0.1", 8003),
        ("127.0.0.1", 8004)
    ]

    # Criar nós
    nós = [FileTransferClient(ip, port) for ip, port in lista_ip_porta]

    # Arquivos a serem enviados
    files_to_send = [
        "upload/file1.txt",
        "upload/file2.txt",
        "upload/file3.txt",
        "upload/file4.txt",
        "upload/file5.txt"
    ]

    # Enviar arquivos
    for i, nó in enumerate(nós):
        destino_ip, destino_port = nós[(i + 1) % len(nós)].ip, nós[(i + 1) % len(nós)].port
        nó.send_file(destino_ip, destino_port, files_to_send[i])
        time.sleep(2)  # Esperar para garantir a conclusão da transferência

    # Receber arquivos
    for i, nó in enumerate(nós):
        destino_ip, destino_port = nós[(i + 1) % len(nós)].ip, nós[(i + 1) % len(nós)].port
        save_path = f"download/downloaded_file{i + 1}.txt"
        nó.receive_file(destino_ip, destino_port, os.path.basename(files_to_send[i]), save_path)
        time.sleep(2)  # Esperar para garantir a conclusão da transferência
