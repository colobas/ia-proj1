from search import *
from copy import deepcopy as copy

class Node:
    def __init__(self, id):
        self.neighbours = dict() # keys = nodes, values = edge costs
        self.id = id
    def __repr__(self):
        return "{0}".format(self.id)

class Stack(Node):
    def __init__(self, id, size):
        Node.__init__(self,id)
        self.size = size
        self.casks = []
        self.space_left = size

class Exit(Node):
    def __init__(self):
        Node.__init__(self, 'EXIT')

class Cask:
    def __init__(self, id, weight, length):
        self.id = id
        self.weight = weight
        self.length = length
    def __repr__(self):
        return "C{0}".format(self.id)

class HCB:
    def __init__(self, filename, goalCask):
        self.casks = dict()
        self.nodes = dict()
        self.nodes['EXIT'] = Exit()
        self.goalCask = goalCask
        self.initial_state = HCBStateRepresentation(None, None, 0, None, self.nodes['EXIT'].id, None)
        lines = []
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
        except:
            raise IOError

        for line in lines:
            l = line.split(" ")
            if l[0][0] == 'C':
                cask_id = l[0][1:]
                cask_length = int(l[1])
                cask_weight = float(l[2])
                self.casks[cask_id] = Cask(cask_id, cask_length, cask_weight)

            elif l[0][0] == 'S':
                stack_id = l[0]
                stack_size = int(l[1])
                casks = l[2:]
                for cask in casks:
                    stack.casks.append(cask[1:])

                self.initial_state.stacks[str(stack)] = stack
                self.nodes[str(stack)] = Stack(stack_id, stack_size)

            elif l[0][0] == 'E':
                if not l[1] in self.nodes:
                    if l[1] != 'EXIT':
                        self.nodes[l[1]] = Node(l[1])
                if not l[2] in self.nodes:
                    if l[2] != 'EXIT':
                        self.nodes[l[2]] = Node(l[2])

                self.nodes[l[1]].neighbours[l[2]] = int(l[3]) # add node with id = l[2] to neighbour list of node with id = l[1]
                self.nodes[l[2]].neighbours[l[1]] = int(l[3]) # vice versa

        self.initial_state.hcb = self
        self.initial_state.setup()

class HCBStateRepresentation(StateRepresentation):
    def __init__(self, parent, hcb, cost, stacks, CTS_pos, cask_on_CTS, prev_operation):
        self.parent = parent
        self.operations = []
        self.stacks = stacks
        self.CTS_pos = CTS_pos
        self.cask_on_CTS = cask_on_CTS
        self.cost = cost # cost of the step taken to get here. we might not need this
        self.prev_operation = prev_operation
        if hcb != None:
            self.hcb = hcb
            self.setup()

    def checksol(self):
        if self.cask_on_CTS == hcb.goalCask and self.CTS_pos == hcb.nodes['EXIT'].id:
            return cost
        else:
            return -1

    def setup(self): #definir operacoes possiveis deste nó
        if type(self.CTS_pos) == Stack and self.cask_on_CTS != None and prev_operation != "load": #undoing previous operation not allowed
            if self.CTS_pos.space_left >= self.cask_on_CTS.length: # if cask fits in stack
                fcost = 1 + hcb.casks[cask_on_CTS].weigh
                self.operations.append({
                            'function' : self.unload, 
                            'description' : "unload {0} {1} {2}".format(self.cask_on_CTS,self.CTS_pos, fcost), 
                            'cost' : fcost
                })
        
        elif type(hcb.nodes[self.CTS_pos]) == Stack and self.cask_on_CTS == None and prev_operation != "unload": #undoing previous operation not allowed
            if hcb.nodes[self.CTS_pos].space_left != hcb.nodes[self.CTS_pos].size: # if stack isn't empty
                fcost = 1 + hcb.casks[cask_on_CTS].weight
                self.operations.append({
                            'function' : self.load, 
                            'description' : "load {0} {1} {2}".format(self.cask_on_CTS, self.CTS_pos, fcost), 
                            'cost' : fcost
                })

        for neighbour in hcb.nodes[self.CTS_pos].neighbours:
            if not (neighbour == parent.CTS_pos and prev_operation == "move"): #moving back not allowed
                fcost = hcb.nodes[self.CTS_pos].neighbours[to]
                def move_to_neighbour():
                    return self.move(neighbour)
                self.operations.append({
                            'function' : move_to_neighbour, 
                            'description' : "move {0} {1} {2}".format(self.CTS_pos, self.nodes[neighbour].id, fcost), 
                            'cost' : fcost
                })

    def move(self, to):
        if self.cask_on_CTS == None:
            next_cost = hcb.nodes[self.CTS_pos].neighbours[to]
        else:
            next_cost = (1 + self.cask_on_CTS.weight)*self.CTS_pos.neighbours[to]
        
        next_CTS_pos = self.nodes[to].id

        next_stacks = copy(self.stacks)
        child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, next_CTS_pos, self.cask_on_CTS, "move")
        return child

    def unload(self):
        next_cost = 1 + hcb.casks[cask_on_CTS].weight
        next_stacks = copy(self.stacks)
        next_CTS_pos = self.CTS_pos
        next_stacks[self.CTS_pos].casks.append(self.cask_on_CTS)
        next_stacks[self.CTS_pos].space_left -= hcb.nodes[cask_on_CTS].length
        child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, self.CTS_pos, None, "unload")
        return child

    def load(self):
        next_cost = 1 + hcb.casks[cask_on_CTS].weight
        next_stacks = copy(self.stacks)
        next_cask_on_CTS = next_stacks[self.CTS_pos].casks.pop()
        next_stacks[self.CTS_pos].space_left += hcb.casks[next_cask_on_CTS].length
        child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, self.CTS_pos, next_cask_on_CTS, "load")
        return child