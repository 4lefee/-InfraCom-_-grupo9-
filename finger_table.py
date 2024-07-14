class FingerTable:
    def __init__(self, node):
        self.node = node
        self.table = [None] * 4

    def update(self):
        for i in range(len(self.table)):
            finger_id = (self.node.id + 2 ** i) % (2 ** 4)
            self.table[i] = self.node.find_successor(finger_id)

    def get_closest_preceding_node(self, key):
        for i in range(len(self.table) - 1, -1, -1):
            if self.table[i] is not None and self.node.id < self.table[i].id < key:
                return self.table[i]
        return self.node
