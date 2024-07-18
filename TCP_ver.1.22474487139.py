import socket
import os

class Node:
    def __init__(self, ip, port, fila, arquivo):
        self.ip = ip
        self.port = port
        self.socket = None
        self.next_node = None
        self.fila = fila
        self.arquivo = arquivo

    def create_socket(self):
        if self.socket is not None:
            self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_file_request(self, servidor):
        try:
            self.create_socket()
            self.socket.connect(servidor)
            self.socket.sendall(b"REQUEST_FILE")
            self.socket.close()
        except Exception as e:
            print(f"Erro ao enviar requisição de arquivo: {e}")

    def send_file_content(self, conn):
        try:
            with open(self.arquivo, 'rb') as file:
                data = file.read()
                conn.sendall(data)
            conn.close()
        except Exception as e:
            print(f"Erro ao enviar conteúdo do arquivo: {e}")

    def receive_file_content(self):
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
        try:
            self.create_socket()
            self.socket.bind((self.ip, self.port))
            self.socket.listen(20)
        except Exception as e:
            print(f"Erro ao ligar o socket: {e}")

    def close(self):
        if self.socket is not None:
            self.socket.close()

    def buscar_arquivo(self, no_inicial, no_arquivo, grupo_nos, no_solicitante):
        if no_inicial == no_arquivo:
            return "O arquivo já está salvo localmente"

        elif self != grupo_nos[no_arquivo]:
            try:
                print(f"Enviando requisição para o próximo nó {self.next_node.ip}:{self.next_node.port}")
                self.send_file_request((self.next_node.ip, self.next_node.port))
                file_content = self.next_node.buscar_arquivo(no_inicial, no_arquivo, grupo_nos, no_solicitante)
                return file_content
            except Exception as e:
                print(f"Erro ao buscar arquivo: {e}")
                return None
        else:
            try:
                print(f"Recebendo arquivo do nó {self.fila + 1}")
                file_content = self.receive_file_content()
                self.save_file(file_content, no_solicitante)
                return file_content
            except Exception as e:
                print(f"Erro ao buscar arquivo: {e}")
                return None

    def save_file(self, file_content, no_solicitante):
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
    lista_ip_porta = [
        ("127.0.0.2", 65515, 1, "Hello.txt"),
        ("127.0.0.1", 6000, 0, "World.txt"),
        ("127.0.0.3", 8900, 2, "Arquivo.py"),
        ("127.0.0.4", 4570, 3, "Materias.txt"),
        ("127.0.0.5", 63200, 4, "Jogo.exe")
    ]

    nós = [Node(ip, port, fila, arquivo) for ip, port, fila, arquivo in lista_ip_porta]

    for i, nó in enumerate(nós):
        nó.next_node = nós[(i + 1) % len(nós)]

    itens = [("Hello.txt", 0), ("World.txt", 1), ("Arquivo.py", 2), ("Materias.txt", 3), ("Jogo.exe", 4)]

    print("Arquivos disponíveis:")
    for item in itens:
        print(item[0])

    for nó in nós:
        nó.bind_socket()

    no_inicial = None
    while no_inicial is None:
        no_inicial_str = input("Qual o nó inicial ? ")
        if no_inicial_str.isdigit():
            no_inicial = int(no_inicial_str) - 1
            if not (0 <= no_inicial < len(nós)):
                print(f"Por favor, escolha um número entre 1 e {len(nós)}.")
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
            for nó in nós:
                nó.close()
                nó.bind_socket()

            file_content = nós[no_inicial].buscar_arquivo(no_inicial, no_file, nós, no_inicial)
            if file_content:
                print(f"Arquivo recebido do nó {no_file + 1}")
            else:
                print(f"Erro ao buscar arquivo do nó {no_file + 1}")

    for nó in nós:
        nó.close()
