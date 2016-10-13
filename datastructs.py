class Node:
    def __init__(self, id):
        self.neighbours = dict() # keys = nodes, values = edge costs
        self.id = id
    def __repr__(self):
        return "{0}".format(self.id)

class Cask:
    def __init__(self, weight, length):
        self.weight = weight
        self.length = length

class Stack(Node):
    def __init__(self, id, size):
        Node.__init__(self,id)
        self.size = size
        self.casks = dict()
        self.occup = 0
    def __repr__(self):
        return "S{0}".format(self.id)

class Exit(Node):
    pass

class Cask:
    def __init__(self, id, weight, length):
        self.id = id
        self.weight = weight
        self.length = length
    def __repr__(self):
        return "C{0}".format(self.id)

class Graph:
    def __init__(self, filename):
        self.casks = dict()
        self.nodes = dict()

        lines = []
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
        except:
            raise IOError

        for line in lines:
            l = line.split(" ")
            if l[0] == 'C':
                cask_id = l[0][1:]
                cask_length = int(l[1])
                cask_weight = float(l[2])
                self.casks[cask_id] = Cask(cask_id, cask_length, cask_weight)

            elif l[0] == 'S':
                stack_id = l[0][1:]
                stack_size = int(l[1])
                stack = Stack(stack_id, stack_size)
                casks = l[2:]
                for cask in casks:
                    stack.casks[cask[1:]] = self.casks[cask[1:]]
                self.nodes[str(stack)] = stack

            elif l[0] == 'E':
                if not l[1] in self.nodes:
                    if l[1] != 'EXIT':
                        self.nodes[l[1]] = Node(l[1])
                    else:
                        self.nodes['EXIT'] = Exit()
                if not l[2] in self.nodes:
                    if l[2] != 'EXIT':
                        self.nodes[l[2]] = Node(l[2])
                    else:
                        self.nodes['EXIT'] = Exit()

                self.nodes[l[1]][l[2]] = self.nodes[l[2]] # add node with id = l[2] to neighbour list of node with id = l[1]
                self.nodes[l[1]][l[2]] = self.nodes[l[1]] # vice versa
