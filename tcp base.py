import socket
import os

class Node:
    def __init__(self, ip, port, fila, arquivo):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.next_node = None
        self.fila = fila
        self.arquivo = arquivo

    def send(self, data, servidor):
        self.socket.sendto(data.encode('utf-8'), servidor)

    def receive(self):
        data, addr = self.socket.recvfrom(2048)
        return data.decode()

    def bind_socket(self):
        self.socket.bind((self.ip, self.port))
        self.socket.listen(20) 

    def close(self):
        self.socket.close()

    def connect(self, servidor):
        self.socket.connect(servidor)

    def buscar_arquivo(self, no_inicial, no_arquivo, grupo_nos):
        if no_inicial == no_arquivo:
            return "O arquivo já está salvo localmente"

        elif self != grupo_nos[no_arquivo]:
            try:
                    self.send("BUSCAR_ARQUIVO", (self.next_node.ip, self.next_node.port))
                    message = self.next_node.buscar_arquivo(no_inicial, no_arquivo, grupo_nos)
                    self.send(message, (self.next_node.ip, self.next_node.port))
                    return self.receive()
            except Exception as e:
                print(f"Erro ao buscar arquivo: {e}")

        else:
            try: 
                    self.send("ENVIAR_ARQUIVO", (self.next_node.ip, self.next_node.port))
                    file_content = self.receive()

                    current_dir = os.getcwd()

                    folder_name = f"Node_{self.fila + 1}"
                    folder_path = os.path.join(current_dir, folder_name)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

            
                    file_name = self.arquivo
                    file_path = os.path.join(folder_path, file_name)
                    with open(file_path, 'w') as file:
                        file.write(file_content)

                    return f"Arquivo salvo em {folder_name}/{file_name}"
            except Exception as e:
                print(f"Erro ao buscar arquivo: {e}")

if __name__ == "__main__":
    lista_ip_porta = [
        ("127.0.0.1", 8010, 0, "Hello.txt"),
        ("127.0.0.2", 8011, 1, "World.txt"),
        ("127.0.0.3", 8012, 2, "Arquivo.py"),
        ("127.0.0.4", 8013, 3, "Materias.txt"),
        ("127.0.0.5", 8014, 4, "Jogo.exe")
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
            no_inicial = int(no_inicial_str)
            if not (1 <= no_inicial <= len(nós)):
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
            recebimento = nós[no_inicial - 1].buscar_arquivo(no_inicial - 1, no_file, nós)
            if recebimento:
                print(f"Arquivo recebido: {recebimento}, do nó {no_file + 1}")
            else:
                print(f"Erro ao buscar arquivo do nó {no_file + 1}")

    for nó in nós:
        nó.close()
