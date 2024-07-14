import socket
import threading
import hashlib
import os
import time
from create_nodes import Node
from finger_table import FingerTable


class DHTNode(Node):
    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.id = self.hash_function(f"{ip}:{port}")
        self.data_store = {}
        self.predecessor = None
        self.successor = None
        self.finger_table = FingerTable(self)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)

    def hash_function(self, key):
        hash_value = hashlib.sha256(key.encode()).hexdigest()
        return int(hash_value, 16) % (2 ** 4)

    def start(self):
        threading.Thread(target=self.listen).start()
        threading.Thread(target=self.fix_fingers).start()  # inicializar a atualização periódica da Finger Table

    def listen(self):
        print(f'Node {self.ip}:{self.port} listening...')
        while True:
            connection, address = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(connection,)).start()

    def handle_client(self, connection):
        while True:
            try:
                data = connection.recv(1024).decode()
                if not data:
                    break
                print(f"Mensagem recebida: {data}")
                self.process_request(data, connection)
            except OSError as e:
                print(f"Erro de socket: {e}")
                break
        connection.close()

    def process_request(self, data, connection):
        parts = data.split()
        command = parts[0]
        if command == 'PUT':
            _, key, value = parts
            self.put(key, value)
        elif command == 'GET':
            _, key = parts
            value = self.get(key)
            connection.send(value.encode())
        elif command == 'PUTFILE':
            _, key, file_size = parts
            self.put_file(connection, key, int(file_size))
        elif command == 'GETFILE':
            _, key = parts
            self.get_file(connection, key)

    def put(self, key, value):
        hash_key = self.hash_function(key)
        responsible_node = self.find_successor(hash_key)
        if responsible_node.id == self.id:
            self.data_store[key] = value
            print(f'Node {self.id} stored key {key} with value {value}')
        else:
            self.send_request(responsible_node, f'PUT {key} {value}')

    def get(self, key):
        hash_key = self.hash_function(key)
        responsible_node = self.find_successor(hash_key)
        if responsible_node.id == self.id:
            return self.data_store.get(key, 'Key not found')
        else:
            return self.send_request(responsible_node, f'GET {key}')

    def put_file(self, connection, key, file_size):
        hash_key = self.hash_function(key)
        responsible_node = self.find_successor(hash_key)
        if responsible_node.id == self.id:
            file_data = connection.recv(file_size)
            os.makedirs('download', exist_ok=True)
            with open(f'download/{key}', 'wb') as file:
                file.write(file_data)
            print(f'Node {self.id} stored file {key}')
        else:
            self.send_request_with_file(responsible_node, connection, key, file_size)

    def get_file(self, connection, key):
        hash_key = self.hash_function(key)
        responsible_node = self.find_successor(hash_key)
        if responsible_node.id == self.id:
            try:
                with open(f'download/{key}', 'rb') as file:
                    file_data = file.read()
                connection.sendall(file_data)
                print(f'Node {self.id} sent file {key}')
            except FileNotFoundError:
                connection.send(b'File not found')
        else:
            self.send_request(responsible_node, f'GETFILE {key}')

    def send_request_with_file(self, node, connection, key, file_size):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((node.ip, node.port))
        client.send(f'PUTFILE {key} {file_size}'.encode())
        file_data = connection.recv(file_size)
        client.sendall(file_data)
        client.close()

    def find_successor(self, key):
        if self.successor is None or self.id == key:
            return self
        if self.id < key <= self.successor.id:
            return self.successor
        return self.finger_table.get_closest_preceding_node(key)

    def send_request(self, node, request):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((node.ip, node.port))
        client.send(request.encode())
        response = client.recv(1024).decode()
        client.close()
        return response

    def fix_fingers(self):
        while True:
            self.finger_table.update()
            time.sleep(10)


if __name__ == "__main__":
    nó_dht = DHTNode("127.0.0.1", 8000)
    nó_dht.start()
    while True:
        time.sleep(1)
