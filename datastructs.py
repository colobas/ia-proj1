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
	def __repr__(self):
		return "{0} {1}".format(self.id, tuple(sorted(self.casks)))
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
		self.initial_state = HCBStateRepresentation(None, None, 0, 0, dict(), self.nodes['EXIT'].id, None, "")
		lines = []
		try:
			with open(filename, "r") as f:
				lines = f.readlines()
		except:
			raise IOError

		for line in lines:
			l = line.replace('\n', '').split(" ")
			if l[0][0] == 'C':
				cask_id = l[0]
				cask_length = int(l[1])
				cask_weight = float(l[2])
				self.casks[cask_id] = Cask(cask_id, cask_weight, cask_length)

			elif l[0][0] == 'S':
				stack_id = l[0]
				stack_size = int(l[1])
				stack = Stack(stack_id, stack_size)
				casks = l[2:]
				for cask in casks:
					stack.casks.append(cask)
					stack.space_left-= self.casks[cask].length

				self.initial_state.stacks[stack_id] = stack
				self.nodes[stack_id] = Stack(stack_id, stack_size)

			elif l[0][0] == 'E':
				if not l[1] in self.nodes:
					if l[1] != 'EXIT':
						self.nodes[l[1]] = Node(l[1])
				if not l[2] in self.nodes:
					if l[2] != 'EXIT':
						self.nodes[l[2]] = Node(l[2])

				self.nodes[l[1]].neighbours[l[2]] = float(l[3]) # add node with id = l[2] to neighbour list of node with id = l[1]
				self.nodes[l[2]].neighbours[l[1]] = float(l[3]) # vice versa

		self.initial_state.hcb = self
		self.initial_state.setup()

class HCBStateRepresentation(StateRepresentation):
	def __init__(self, parent, hcb, fcost, gcost, stacks, CTS_pos, cask_on_CTS, prev_operation):
		self.parent = parent
		self.operations = dict()
		self.stacks = stacks
		self.CTS_pos = CTS_pos
		self.cask_on_CTS = cask_on_CTS
		self.fcost = fcost # cost of the step taken to get here. we might not need this
		self.gcost = gcost
		self.prev_operation = prev_operation
		if hcb != None:
			self.hcb = hcb
			self.setup()

	def __repr__(self):
		s = ""
		for st in sorted(self.stacks.items()):
			s += "{0}".format(st)
		return "{0} {1} {2}".format(s, self.CTS_pos, self.cask_on_CTS)

	def __hash__(self):
		return hash(self.__repr__())

	def __eq__(self, other):
		return self.__hash__() == other.__hash__()

	def checksol(self):
		if self.cask_on_CTS == self.hcb.goalCask and self.CTS_pos == self.hcb.nodes['EXIT'].id:
			return self.fcost
		else:
			return -1

	def setup(self): #definir operacoes possiveis deste nó
		if type(self.hcb.nodes[self.CTS_pos]) == Stack and self.cask_on_CTS != None and self.prev_operation != "load": #undoing previous operation not allowed
			if self.stacks[self.CTS_pos].space_left >= self.hcb.casks[self.cask_on_CTS].length: # if cask fits in stack
				fcost = 1 + self.hcb.casks[self.cask_on_CTS].weight
				gcost = 0
				self.operations["unload"] = {
							'function' : self.unload, 
							'description' : "unload {0} {1} {2}".format(self.cask_on_CTS, self.CTS_pos, fcost), 
							'fcost' : fcost + self.fcost,
							'gcost' : gcost
				}
		
		elif type(self.hcb.nodes[self.CTS_pos]) == Stack and self.cask_on_CTS == None and self.prev_operation != "unload": #undoing previous operation not allowed
			if self.stacks[self.CTS_pos].space_left != self.stacks[self.CTS_pos].size: # if stack isn't empty
				cask_on_CTS = self.hcb.casks[self.stacks[self.CTS_pos].casks[-1]]
				fcost = 1 + cask_on_CTS.weight
				gcost = 0
				self.operations["load"] = {
							'function' : self.load, 
							'description' : "load {0} {1} {2}".format(cask_on_CTS.id, self.CTS_pos, fcost), 
							'fcost' : fcost + self.fcost,
							'gcost' : gcost
				}

		for neighbour in self.hcb.nodes[self.CTS_pos].neighbours:
			if (self.parent == None) or not ((neighbour == self.parent.CTS_pos) and "move" in self.prev_operation): #moving back not allowed
				if self.cask_on_CTS == None:
					fcost = self.hcb.nodes[self.CTS_pos].neighbours[neighbour]
				else:
					fcost = (1 + self.hcb.casks[self.cask_on_CTS].weight)*self.hcb.nodes[self.CTS_pos].neighbours[neighbour]

				gcost = 0
				def move_to_neighbour(neighbour=neighbour):
					return self.move(neighbour)
				move_key = "move{0}".format(neighbour)
				self.operations[move_key]= {
							'function' : move_to_neighbour, 
							'description' : "move {0} {1} {2}".format(self.CTS_pos, self.hcb.nodes[neighbour].id, fcost), 
							'fcost' : fcost + self.fcost,
							'gcost' : gcost
				}

	def move(self, to):
		if self.cask_on_CTS == None:
			next_cost = self.hcb.nodes[self.CTS_pos].neighbours[to]
		else:
			next_cost = (1 + self.hcb.casks[self.cask_on_CTS].weight)*self.hcb.nodes[self.CTS_pos].neighbours[to]
		
		next_cost = self.fcost + next_cost
		next_CTS_pos = self.hcb.nodes[to].id

		next_stacks = copy(self.stacks)
		child = HCBStateRepresentation(self, self.hcb, next_cost, 0, next_stacks, next_CTS_pos, self.cask_on_CTS, "move{0}".format(to))
		return child

	def unload(self):
		next_cost = 1 + self.hcb.casks[self.cask_on_CTS].weight + self.fcost
		next_stacks = copy(self.stacks)
		next_CTS_pos = self.CTS_pos
		next_stacks[self.CTS_pos].casks.append(self.cask_on_CTS)
		next_stacks[self.CTS_pos].space_left -= self.hcb.casks[self.cask_on_CTS].length
		child = HCBStateRepresentation(self, self.hcb, next_cost, 0, next_stacks, self.CTS_pos, None, "unload")
		return child

	def load(self):
		next_cost = 1 + self.hcb.casks[self.stacks[self.CTS_pos].casks[-1]].weight + self.fcost
		next_stacks = copy(self.stacks)
		next_cask_on_CTS = next_stacks[self.CTS_pos].casks.pop()
		next_stacks[self.CTS_pos].space_left += self.hcb.casks[next_cask_on_CTS].length
		child = HCBStateRepresentation(self, self.hcb, next_cost, 0, next_stacks, self.CTS_pos, next_cask_on_CTS, "load")
		return child
