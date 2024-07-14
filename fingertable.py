class FingerTable:
    def __init__(self, node, num_bits=4):
        self.node = node
        self.num_bits = num_bits
        self.table = {}
        self.build_table()

    def build_table(self):
        for i in range(self.num_bits):
            start = (self.node.id + 2**i) % (2**self.num_bits)
            self.table[start] = None

    def update(self, all_nodes):
        for start in self.table.keys():
            self.table[start] = self.find_successor(start, all_nodes)

    def find_successor(self, id, all_nodes):
        sorted_nodes = sorted(all_nodes, key=lambda n: n.id)
        for node in sorted_nodes:
            if node.id >= id:
                return node
        return sorted_nodes[0]

    def __str__(self):
        return str(self.table)
