import socket
import os
import time
import hashlib

class Node:
    def __init__(self, ip, port, fila, arquivo, total_nodes):
        self.ip = ip
        self.port = port
        self.fila = fila
        self.arquivo = arquivo
        self.total_nodes = total_nodes
        self.id = self.hash_function(f"{ip}:{port}")
        self.socket = None
        self.next_node = None
        self.finger_table = [None] * total_nodes

    def hash_function(self, key):
        """Calcula um identificador usando SHA-1 e retorna um valor entre 0 e total_nodes-1."""
        return int(hashlib.sha1(key.encode()).hexdigest(), 16) % self.total_nodes

    def create_socket(self):
        """Cria um novo socket TCP para o nó."""
        if self.socket is not None:
            self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_file_request(self, servidor):
        """Envia uma solicitação de arquivo para o nó servidor."""
        try:
            self.create_socket()
            self.socket.connect(servidor)
            self.socket.sendall(b"REQUEST_FILE")
            self.socket.close()
        except Exception as e:
            print(f"Erro ao enviar requisição de arquivo: {e}")

    def send_file_content(self, conn):
        """Envia o conteúdo de um arquivo para o nó conectado."""
        try:
            with open(self.arquivo, 'rb') as file:
                data = file.read()
                conn.sendall(data)
            conn.close()
        except Exception as e:
            print(f"Erro ao enviar conteúdo do arquivo: {e}")

    def receive_file_content(self):
        """Recebe o conteúdo de um arquivo de um nó conectado."""
        try:
            conn, addr = self.socket.accept()
            file_content = b""
            while True:
                data = conn.recv(2048)
                if not data:
                    break
                file_content += data
            conn.close()
            return file_content
        except Exception as e:
            print(f"Erro ao receber conteúdo do arquivo: {e}")
            return None

    def bind_socket(self):
        """Liga o socket do nó para aguardar conexões entrantes."""
        try:
            self.create_socket()
            self.socket.bind((self.ip, self.port))
            self.socket.listen(20)
        except Exception as e:
            print(f"Erro ao ligar o socket: {e}")

    def close(self):
        """Fecha o socket do nó."""
        if self.socket is not None:
            self.socket.close()

    def buscar_arquivo(self, no_inicial, no_arquivo, grupo_nos, no_solicitante):
        """Busca um arquivo na rede P2P começando pelo nó inicial usando a finger table."""
        if no_inicial == no_arquivo:
            return "O arquivo já está salvo localmente"

        target_id = grupo_nos[no_arquivo].id
        successor = self.find_successor(target_id, grupo_nos)

        if successor.id == self.id:
            try:
                print(f"Recebendo arquivo do nó {self.fila + 1}")
                start_time = time.time()
                file_content = self.receive_file_content()
                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"Tempo para receber o arquivo: {elapsed_time:.4f} segundos")
                self.save_file(file_content, no_solicitante)
                return file_content
            except Exception as e:
                print(f"Erro ao buscar arquivo: {e}")
                return None
        else:
            try:
                print(f"Enviando requisição para o próximo nó {successor.ip}:{successor.port}")
                self.send_file_request((successor.ip, successor.port))
                file_content = successor.buscar_arquivo(no_inicial, no_arquivo, grupo_nos, no_solicitante)
                return file_content
            except Exception as e:
                print(f"Erro ao buscar arquivo: {e}")
                return None

    def find_successor(self, id, grupo_nos):
        """Encontra o sucessor do identificador id usando a finger table."""
        if self.id == id:
            return self

        if self.is_in_interval(id, self.id, self.next_node.id):
            return self.next_node

        node = self.closest_preceding_node(id)
        return node.find_successor(id, grupo_nos)

    def closest_preceding_node(self, id):
        """Encontra o nó mais próximo precedendo o identificador id na finger table."""
        for i in range(len(self.finger_table) - 1, -1, -1):
            if self.finger_table[i] and self.is_in_interval(self.finger_table[i].id, self.id, id):
                return self.finger_table[i]
        return self

    def is_in_interval(self, id, start, end):
        """Verifica se um identificador id está no intervalo (start, end]."""
        if start < end:
            return start < id <= end
        else:
            return start < id or id <= end

    def save_file(self, file_content, no_solicitante):
        """Salva o conteúdo de um arquivo recebido em uma pasta específica para o nó."""
        try:
            current_dir = os.getcwd()
            folder_name = f"Node_{no_solicitante + 1}"
            folder_path = os.path.join(current_dir, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            file_name = self.arquivo
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'wb') as file:
                file.write(file_content)

            print(f"Arquivo salvo em {folder_name}/{file_name}")
        except Exception as e:
            print(f"Erro ao salvar arquivo: {e}")

if __name__ == "__main__":
    total_nodes = 5

    lista_ip_porta = [
        ("127.0.0.2", 65515, 1, "Hello.txt"),
        ("127.0.0.1", 6000, 0, "World.txt"),
        ("127.0.0.3", 8900, 2, "Arquivo.txt"),
        ("127.0.0.4", 4570, 3, "Materias.txt"),
        ("127.0.0.5", 63200, 4, "Jogo.txt")
    ]

    nos = [Node(ip, port, fila, arquivo, total_nodes) for ip, port, fila, arquivo in lista_ip_porta]

    for i, no in enumerate(nos):
        no.next_node = nos[(i + 1) % len(nos)]

    for no in nos:
        for i in range(total_nodes):
            no.finger_table[i] = nos[(no.id + 2**i) % len(nos)]

    itens = [("Hello.txt", 0), ("World.txt", 1), ("Arquivo.txt", 2), ("Materias.txt", 3), ("Jogo.txt", 4)]

    print("Arquivos disponíveis:")
    for item in itens:
        print(item[0])

    for no in nos:
        no.bind_socket()

    no_inicial = None
    while no_inicial is None:
        no_inicial_str = input("Qual o nó inicial ? ")
        if no_inicial_str.isdigit():
            no_inicial = int(no_inicial_str) - 1
            if not (0 <= no_inicial < len(nos)):
                print(f"Por favor, escolha um número entre 1 e {len(nos)}.")
                no_inicial = None
        else:
            print("Por favor, digite um número válido.")

    while True:
        solicitacao = input("Qual arquivo você deseja buscar? ")
        if solicitacao.lower() == "terminar":
            break

        no_file = None
        for item in itens:
            if solicitacao.lower() in item[0].lower():
                no_file = item[1]
                break

        if no_file is None:
            print(f"Arquivo '{solicitacao}' não encontrado.")
        else:
            for no in nos:
                no.close()
                no.bind_socket()

            file_content = nos[no_inicial].buscar_arquivo(no_inicial, no_file, nos, no_inicial)
            if file_content:
                print(f"Arquivo recebido do nó {no_file + 1}")
            else:
                print(f"Erro ao buscar arquivo do nó {no_file + 1}")

    for no in nos:
        no.close()
