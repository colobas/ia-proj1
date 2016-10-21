from search import *
from copy import copy

class Node:
	"""
	Defines a Node in the HCB graph. Might be a Stack, a simple Node, or an Exit point
	"""
	def __init__(self, id):
		self.neighbours = dict() # keys = nodes, values = edge costs
		self.id = id
	def __repr__(self):
		return "{0}".format(self.id)

class Stack(Node):
	"""
	Extends the Node class to implement a Stack
	"""
	def __init__(self, id, size):
		Node.__init__(self,id)
		self.size = size


class Exit(Node):
	"""
	Extends the Node class to implement an Exit point
	"""
	def __init__(self):
		Node.__init__(self, 'EXIT')

class Cask:
	"""
	Defines a Cask object. Its content never changes once initialized.
	"""
	def __init__(self, id, weight, length):
		self.id = id
		self.weight = weight
		self.length = length

class HCB:
	"""
	Defines the static part of the problem -> The HCB graph and the data structures where information about the casks and nodes is stored.
	In the State Representation, we use the objects' ids to fetch their info when we need it (e.g. getting a cask's weight)
	"""
	def __init__(self, filename, goalCask):
		"""
		Initialization of the problem. Here we read the file and store its information in the appropriate structures. We also create the
		State representation of the initial state.
		"""
		self.casks = dict()
		self.nodes = dict()
		self.nodes['EXIT'] = Exit()
		self.paths = dict()
		self.goalCask = goalCask
		self.initial_state = HCBStateRepresentation(None, self, 0, dict(), dict(), self.nodes['EXIT'].id, None, "", True)
		lines = []
		try:
			with open(filename, "r") as f:
				lines = f.readlines()
		except:
			raise IOError
		
		cask_lines = []
		stack_lines = []
		edge_lines = []
		for line in lines:
			l = line.replace('\n', '').split(" ")
			if l == '':
				continue
			if l[0][0] == 'C':
				cask_lines.append(l)
			elif l[0][0] == 'S':
				stack_lines.append(l)
			elif l[0][0] == 'E':
				edge_lines.append(l)



		for l in cask_lines: # Creation of a cask. It will be stored in a dictionary, where its key is the id.
			cask_id = l[0]
			cask_length = int(l[1])
			cask_weight = float(l[2])
			self.casks[cask_id] = Cask(cask_id, cask_weight, cask_length)

		for l in stack_lines:
			stack_id = l[0]
			stack_size = int(l[1])
			self.nodes[stack_id] = Stack(stack_id, stack_size)
			self.initial_state.stacks[stack_id] = (stack_size, None)
			casks = l[2:]
			for cask in casks:
				self.initial_state.doUnload(stack_id, cask, self.initial_state.stacks, self.initial_state.casks)

		for l in edge_lines:
			if not l[1] in self.nodes:
				if l[1] != 'EXIT':
					self.nodes[l[1]] = Node(l[1])
			if not l[2] in self.nodes:
				if l[2] != 'EXIT':
					self.nodes[l[2]] = Node(l[2])

			self.nodes[l[1]].neighbours[l[2]] = float(l[3]) # add node with id = l[2] to neighbour list of node with id = l[1]
			self.nodes[l[2]].neighbours[l[1]] = float(l[3]) # vice versa
		
		for node in self.nodes.values():
			self.paths[node.id] = dijkstra(self.nodes.values(), node)
		self.initial_state.setup()

class HCBStateRepresentation(StateRepresentation):
	"""
	Class for the representation of States on the search algorithm. This class extends the 'interface' StateRepresentation.
	"""
	def __init__(self, parent, hcb, cost, stacks, casks, CTS_pos, cask_on_CTS, prev_operation, isRoot):
		self.parent = parent # node through each we got here
		self.operations = dict() # operations available to perform on this node
		self.stacks = stacks # state of the stacks on this node
		self.casks = casks
		self.CTS_pos = CTS_pos # position of the CTS. this is an Id, so we need to use it to index the dict in self.hcb.nodes
		self.cask_on_CTS = cask_on_CTS # cask loaded on CTS. (None -> no cask). This is an Id, so we need to use it to index the dict in self.hcb.casks
		self.cost = cost
		self.prev_operation = prev_operation # operation that got us here
		self.hcb = hcb
		if not isRoot: # needed for the instatiation of the initial state, because we instatiate before we've read the file and built the map
			self.setup()


	def __key__(self):
        	return (self.stacks, self.casks, self.CTS_pos, self.cask_on_CTS)

	def __eq__(self, other):
		if other == None:
			return False
		return  self.__key__() == other.__key__()

	def checksol(self):
		return self.cask_on_CTS == self.hcb.goalCask and self.CTS_pos == self.hcb.nodes['EXIT'].id

	def doUnload(self, stack_id, cask_id, stacks, casks):
		casks[cask_id] = (stack_id, stacks[stack_id][1])
		space_left = stacks[stack_id][0] - self.hcb.casks[cask_id].length
		stacks[stack_id] = (space_left, cask_id)

	def doLoad(self, stack_id, stacks, casks):
		top_cask_id = stacks[stack_id][1]
		space_left = stacks[stack_id][0] + self.hcb.casks[top_cask_id].length
		stacks[stack_id] = (space_left, casks[top_cask_id][1])
		casks[top_cask_id] = ('CTS', None)
		return top_cask_id

# The names of the following group of methods are pretty self-explaining, but here are some remarks:
#	-> The methods that check if a given operation is feasible have to check if this operation undoes the previous one, to avoid infinite loops
#	-> self.CTS_pos and self.cask_on_CTS are Ids, so everytime we need info on the object they represent, we have to use these Ids to index the
#	appropriate dicts on the HCB object
#	-> The way we fetch info on the cask to be loaded on the CTS seems strange, but that's because that cask "still isn't" the cask_on_CTS, and
#	so we have to fetch it based on the position of the CTS (i.e. fetch the cask on top of the stack the CTS is in)
#	-> The methods that fetch operation costs are only called after their corresponding operations have been deemed feasible, so there are no
#	feasibility checks inside them

	def unloadIsFeasible(self):
		return type(self.hcb.nodes[self.CTS_pos]) == Stack and self.cask_on_CTS != None and self.prev_operation != "load"

	def caskFitsStack(self):
		return self.stacks[self.CTS_pos][0] >= self.hcb.casks[self.cask_on_CTS].length

	def loadIsFeasible(self):
		return type(self.hcb.nodes[self.CTS_pos]) == Stack and self.cask_on_CTS == None and self.prev_operation != "unload"

	def stackHasCasks(self):
		return self.stacks[self.CTS_pos][0] < self.hcb.nodes[self.CTS_pos].size

	def moveIsFeasible(self, neighbour):
		return (self.parent == None) or not ((neighbour == self.parent.CTS_pos) and "move" in self.prev_operation)

	def getCaskOnThisStack(self):
		cask_id = self.stacks[self.CTS_pos][1]
		return self.hcb.casks[cask_id]

	def getCaskOnCTS(self):
		return self.hcb.casks[self.cask_on_CTS]

	def getLoadCost(self, cask):
		return 1 + cask.weight

	def getUnloadCost(self):
		cask = self.getCaskOnCTS()
		return 1 + cask.weight

	def getMoveCost(self, neighbour):
		edge = self.hcb.nodes[self.CTS_pos].neighbours[neighbour]

		if self.cask_on_CTS == None:
			cost = edge 
		else:
			cask = self.getCaskOnCTS()
			cost = (1 + cask.weight)*edge

		return cost

# ----------------------------------- END OF GROUP OF SELF-EXPLAINING METHODS ------------------------------------



# The following group of methods implements the actual operations to be performed on this node. They're only ever called after they've been deemed feasible,
# so there's no feasibility checks inside them. They each compute the appropriate arguments to instantiate the StateRepresentation of the node created by performing
# that operation and then instantiate and return that node.

	def move(self, to):
		next_cost = self.getMoveCost(to) + self.cost
		next_CTS_pos = self.hcb.nodes[to].id
		next_stacks = copy(self.stacks)
		next_casks = copy(self.casks)
		child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, next_casks, next_CTS_pos, self.cask_on_CTS, "move{0}".format(to), False)
		return child

	def unload(self):
		next_cost = self.getUnloadCost() + self.cost
		next_stacks = copy(self.stacks)
		next_casks = copy(self.casks)
		next_CTS_pos = self.CTS_pos
		
		self.doUnload(self.CTS_pos, self.cask_on_CTS, next_stacks, next_casks)

		child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, next_casks, self.CTS_pos, None, "unload", False)
		return child

	def load(self):
		next_stacks = copy(self.stacks)
		next_casks = copy(self.casks)
		next_cask_on_CTS_id = self.doLoad(self.CTS_pos, next_stacks, next_casks)
		next_cask_on_CTS = self.hcb.casks[next_cask_on_CTS_id]

		next_cost = self.getLoadCost(next_cask_on_CTS) + self.cost

		child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, next_casks, self.CTS_pos, next_cask_on_CTS_id, "load", False)
		return child

# ---------------------------------- END OF OPERATIONS IMPLEMENTATION ------------------------------------------------------
	def heuristic(self):
		if self.cask_on_CTS == self.hcb.goalCask:
			return self.hcb.paths[self.CTS_pos]['EXIT'][0]
		else:
			goalStack = self.casks[self.hcb.goalCask][0]
			return self.hcb.paths[self.CTS_pos][goalStack][0]

	def setup(self):
		"""
		This method computes the operations that can be performed on this node. It stores the corresponding method on the self.operations dict, as well
		as their description and costs.
		"""
		if self.unloadIsFeasible():
			if self.caskFitsStack():
				cost = self.getUnloadCost()
				self.operations["unload"] = {
					'function' : self.unload, 
					'description' : "unload {0} {1} {2}".format(self.cask_on_CTS, self.CTS_pos, cost), 
					'cost' : cost + self.cost,
				}
		
		elif self.loadIsFeasible():
			if self.stackHasCasks():
				cask_on_CTS = self.getCaskOnThisStack() 
				cost = self.getLoadCost(cask_on_CTS)
				self.operations["load"] = {
					'function' : self.load, 
					'description' : "load {0} {1} {2}".format(cask_on_CTS.id, self.CTS_pos, cost), 
					'cost' : cost + self.cost,
				}

		for neighbour in self.hcb.nodes[self.CTS_pos].neighbours:
			if self.moveIsFeasible(neighbour):
				cost = self.getMoveCost(neighbour)

				def move_to_neighbour(neighbour=neighbour): # trick to define a 'move' method for each feasible neighbour, without the need of
					return self.move(neighbour)         # the search algorithm to pass it any arguments

				move_key = "move{0}".format(neighbour)
				self.operations[move_key]= {
					'function' : move_to_neighbour, 
					'description' : "move {0} {1} {2}".format(self.CTS_pos, self.hcb.nodes[neighbour].id, cost), 
					'cost' : cost + self.cost,
				}

def dijkstra(_nodes, initial):
	costs = {initial.id: (0,'')}
	nodes = set(_nodes)

	while nodes:
		min_node = None
		for node in nodes:
			if node.id in costs:
				if min_node is None:
					min_node = node
				elif costs[node.id][0] < costs[min_node.id][0]:
					min_node = node

		if min_node is None:
			break

		nodes.remove(min_node)
		current_weight = costs[min_node.id][0]

		for neighbour_id in min_node.neighbours:
			weight = current_weight + min_node.neighbours[neighbour_id]
			if neighbour_id not in costs or weight < costs[neighbour_id][0]:
				costs[neighbour_id] = (weight, min_node.id)

	return costs
