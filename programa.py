import socket

#ATENÇÃO: TRANFORMEI O CÓDIGO EM UDP PARA PROGRAMAR, É NECESSÁRIO VOLTAR PARA TCP PARA O FINAL DO PROJETO
#cria o nó
class Node:
    #define o ip e a porta do nó + o ponteiro de ligação + a posição na fila + o arquivo que a máquina possui
    def __init__(self, ip, port, fila, arquivo):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.next_node = None
        self.fila = fila
        self.arquivo = arquivo

    #funções auto-explicativas de enviar/receber 
    def send(self, data, servidor):
        self.socket.sendto(data.encode(), servidor)

    def receive(self):
        return self.socket.recvfrom(2048)

    ''' para o tcp
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
    '''
    def bind_socket(self):
        self.socket.bind((self.ip, self.port))
    
    def close(self):
        self.socket.close()

def buscar_arquivo(inicio, no_arquivo, grupo_nos):
    if(inicio == no_arquivo):
        return "O arquivo já está salvo localmente"

    elif(grupo_nos[inicio].next_node != grupo_nos[no_arquivo]):
        
        message, CLAdress =  buscar_arquivo(grupo_nos[inicio].next_node.fila, no_arquivo, grupo_nos)

        message = message.decode()

        grupo_nos[inicio].next_node.send(message, (grupo_nos[inicio].ip, grupo_nos[inicio].port))

        return grupo_nos[inicio].receive()


    else:
        grupo_nos[inicio].next_node.send(grupo_nos[inicio].next_node.arquivo, (grupo_nos[inicio].ip, grupo_nos[inicio].port)) 

        return grupo_nos[inicio].receive()
 
#inicia o funcionamento do código
if __name__ == "__main__":
    #cria a lista de IPs que iremos usar para enviar e receber
    lista_ip_porta = [
        ("127.0.0.1", 8010, 0, "Hello.txt"),
        ("127.0.0.1", 8011, 1, "World.txt"),
        ("127.0.0.1", 8012, 2, "Arquivo.py"),
        ("127.0.0.1", 8013, 3, "Materias.txt"),
        ("127.0.0.1", 8014, 4, "Jogo.exe")
    ]

    #cria os nós e os adiciona em tabelas, agora já temos as conexões individuais!
    nós = [Node(ip, port, fila, arquivo) for ip, port, fila, arquivo in lista_ip_porta]
    for i, nó in enumerate(nós):
        nó.next_node = nós[(i + 1) % len(nós)]  
        #print(f"Nó online: IP={nó.ip}, Porta={nó.port}, Fila = {nó.fila}, Próximo nó: IP={nó.next_node.ip}, Porta={nó.next_node.port}, Fila = {nó.next_node.fila}")
    
    #cria a "tabela" de arquivos que avisa em qual host está cada arquivo
    itens = [("Hello.txt", 1),("World.txt", 2),("Arquivo.py", 3),("Materias.txt", 4),("Jogo.exe", 5)]

    #mostra os arquivos disponíveis:
    print("Arquivos disponíveis:")
    for item in itens:
        print(item[0], end="\n")

    no_inicial = -1
    solicitacao = ""
    no_file = ""

    #todas as máquinas da rede irão dar bind no socket do computador para ser um host
    for nó in nós:
        nó.bind_socket()

    #código rodando indefinidamente para testes
    while (solicitacao.lower() != "terminar"): 

        #define o nó inicial e qual o arquivo solicitado
        while(no_inicial < 1 or no_inicial > 5):
            no_inicial = int(input("Qual o nó inicial? "))
            if(no_inicial < 1 or no_inicial > 5):
                print("Por favor escolha um nó inicial entre 1 e 5")

        solicitacao = input("Qual o arquivo que você deseja buscar? ")
        if(solicitacao.lower() == "terminar"):
            break

        #vai descobrir em qual nó o arquivo está (isso não seria necessário pois a lista está em ordem, mas para automatização e caso a lista esteja randomizada é importante)
        for x in range(0, len(itens)):
            if(solicitacao.lower() in itens[x][0].lower()):
                no_file = itens[x][1]

        try:
            recebimento, endereco = buscar_arquivo(no_inicial - 1, no_file - 1, nós)
            recebimento = recebimento.decode()
            print(f"Arquivo: {recebimento}, recebido da máquina {no_file}")
        except:
            print(buscar_arquivo(no_inicial - 1, no_file - 1, nós))


#quando o código acabar, eles vão liberar o socket do computador para tentar novamente
    for nó in nós:
        nó.close()