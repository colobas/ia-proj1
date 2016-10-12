class Node:
    def __init__(self):
        self.neighbours = dict() # keys = nodes, values = edges

class Cask:
    def __init__(self, weight, length):
        self.weight = weight
        self.length = length

class Stack(Node):
    def __init__(self, size):
        Node.__init__(self)
        self.size = size

class Exit(Node):
    pass

class Cask:
    def __init__(self, weight, length):
        self.weight = weight
        self.length = length


