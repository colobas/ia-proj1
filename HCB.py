from search import *

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
	Extends the Node class to implement a Stack. In fact it just adds a field corresponding to the Stack's size
	"""
	def __init__(self, id, size):
		Node.__init__(self,id)
		self.size = size


class Exit(Node):
	"""
	Extends the Node class to implement an Exit point.
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
		stacks = []
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
			casks = l[2:]
			space_left = stack_size
			for cask in casks:
				space_left -= self.casks[cask].length
			stacks.append((stack_id, space_left, tuple(casks)))

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

		self.initial_state = HCBStateRepresentation(None, self, 0, tuple(stacks), 'EXIT', None, '')

class HCBStateRepresentation(StateRepresentation):
	"""
	Class for the representation of States on the search algorithm. This class extends the 'interface' StateRepresentation.
	"""
	
	def __init__(self, parent, hcb, cost, stacks, CTS_pos, cask_on_CTS, prev_operation):
		self.stacks = stacks # tuple of stack tuples. each stack tuple -> (id, space_left, (Cx,Cy,Cz))
		self.parent = parent # node through each we got here
		self.CTS_pos = CTS_pos # position of the CTS. this is an Id, so we need to use it to index the dict in self.hcb.nodes
		self.cask_on_CTS = cask_on_CTS # cask loaded on CTS. (None -> no cask). This is an Id, so we need to use it to index the dict in self.hcb.casks
		self.cost = cost
		self.prev_operation = prev_operation # operation that got us here
		self.hcb = hcb
		self.initial_state = None

	def __key__(self):
		return (self.stacks, self.CTS_pos, self.cask_on_CTS)

	def __hash__(self):
		return hash(self.__key__())

	def __eq__(self, other):
		if other == None:
			return False
		if self.CTS_pos != other.CTS_pos:
			return False
		elif self.cask_on_CTS != other.cask_on_CTS:
			return False
		elif self.stacks != other.stacks:
			return False
		return True

	def checksol(self): # method to check whether this state is a solution
		return self.cask_on_CTS == self.hcb.goalCask and self.CTS_pos == self.hcb.nodes['EXIT'].id

	def doUnload(self, stack_id, cask_id):
		"""
		Handle the manipulation of the stacks and casks data structures upon the unloading of a cask. stacks and casks are passed
		as arguments because this method is called to prepare the data structures of the State Representation obtained by performing
		this action
		"""
		_stacks = list(self.stacks)

		for i in range(0,len(_stacks)):
			if _stacks[i] == stack_id:
				space_left = _stacks[i][1] - self.hcb.casks[cask_id].length
				_stacks[i] = (stack_id, space_left, tuple(list(_stacks[i][2]).append(cask_id)))
				break

		return tuple(_stacks)


	def doLoad(self, stack_id):
		"""
		Handle the manipulation of the stacks and casks data structures upon the unloading of a cask. stacks and casks are passed
		as arguments because this method is called to prepare the data structures of the State Representation obtained by performing
		this action
		"""
		_stacks = list(self.stacks)
		for i in range(0, len(_stacks)):
			if _stacks[i][0] == stack_id:
				casks = list(_stacks[i][2])
				cask = casks.pop()
				space_left = _stacks[i][1] + self.hcb.casks[cask].length
				_stacks[i] = (stack_id, space_left, tuple(casks))
				break

		return tuple(_stacks), cask


# The names of the following group of methods are pretty self-explaining, but here are some remarks:
#	-> The methods that check if a given operation is feasible have to check if this operation undoes the previous one, to avoid infinite loops
#	-> self.CTS_pos and self.cask_on_CTS are Ids, so everytime we need info on the object they represent, we have to use these Ids to index the
#	appropriate dicts on the HCB object
#	-> The way we fetch info on the cask to be loaded on the CTS seems strange, but that's because that cask "still isn't" the cask_on_CTS, and
#	so we have to fetch it based on the position of the CTS (i.e. fetch the cask on top of the stack the CTS is in)
#	-> The methods that fetch operation costs are only called after their corresponding operations have been deemed feasible, so there are no
#	feasibility checks inside them

	def unloadIsFeasible(self):
		return type(self.hcb.nodes[self.CTS_pos]) == Stack and self.cask_on_CTS != None and self.prev_operation != ord("L")

	def caskFitsStack(self):
		for stack in self.stacks:
			if stack[0] == self.CTS_pos:
				return stack[1] >= self.hcb.casks[self.cask_on_CTS].length

	def loadIsFeasible(self):
		return type(self.hcb.nodes[self.CTS_pos]) == Stack and self.cask_on_CTS == None and self.prev_operation != ord("U")

	def stackHasCasks(self):
		for stack in self.stacks:
			if stack[0] == self.CTS_pos:
				return stack[1] < self.hcb.nodes[self.CTS_pos].size

	def moveIsFeasible(self, neighbour):
		return (self.parent == None) or not ((neighbour == self.parent.CTS_pos) and self.prev_operation) == ord("M")

	def getCaskOnThisStack(self):
		for stack in self.stacks:
			if stack[0] == self.CTS_pos:
				return stack[2][0]

	def getLoadCost(self, cask):
		return 1 + self.hcb.casks[cask].weight

	def getUnloadCost(self):
		return 1 + self.hcb.casks[self.cask_on_CTS].weight

	def getMoveCost(self, neighbour):
		edge = self.hcb.nodes[self.CTS_pos].neighbours[neighbour]

		if self.cask_on_CTS == None:
			cost = edge 
		else:
			cost = self.getUnloadCost()*edge

		return cost

	def getMoveDescription(self):
		cost = self.cost - self.parent.cost
		if self.prev_operation == ord("M"):
			return "move {} {} {}".format(self.parent.CTS_pos, self.CTS_pos, cost)
		elif self.prev_operation == ord("L"):
			return "load {} {} {}".format(self.cask_on_CTS, self.CTS_pos, cost)
		elif self.prev_operation == ord("U"):
			return "unload {} {} {}".format(self.parent.cask_on_CTS, self.CTS_pos, cost)
# ----------------------------------- END OF GROUP OF SELF-EXPLAINING METHODS ------------------------------------



# The following group of methods implements the actual operations to be performed on this node. They're only ever called after they've been deemed feasible,
# so there's no feasibility checks inside them. They each compute the appropriate arguments to instantiate the StateRepresentation of the node created by performing
# that operation and then instantiate and return that node.
	
	def move(self, to):
		next_cost = self.getMoveCost(to) + self.cost
		next_CTS_pos = to
		next_stacks = tuple(self.stacks)
		child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, next_CTS_pos, self.cask_on_CTS, ord("M"))
		return child

	def unload(self):
		next_cost = self.getUnloadCost() + self.cost
		next_stacks = self.doUnload(self.CTS_pos, self.cask_on_CTS)
		child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, self.CTS_pos, None, ord("U"))
		return child

	def load(self):
		next_stacks, next_cask_on_CTS = self.doLoad(self.CTS_pos)
		next_cost = self.getLoadCost(next_cask_on_CTS) + self.cost
		child = HCBStateRepresentation(self, self.hcb, next_cost, next_stacks, self.CTS_pos, next_cask_on_CTS, ord("L"))
		return child

# ---------------------------------- END OF OPERATIONS IMPLEMENTATION ------------------------------------------------------
	def heuristic(self):
		if self.cask_on_CTS == self.hcb.goalCask:
			return self.hcb.paths[self.CTS_pos]['EXIT'][0]
		else:
			goalStack = self.casks[self.hcb.goalCask][0]
			return self.hcb.paths[self.CTS_pos][goalStack][0]

	def expand(self):
		"""
		This method computes the operations that can be performed on this node. It stores the corresponding method on the self.operations dict, as well
		as their description and costs.
		"""
		children = []
		if self.unloadIsFeasible():
			if self.caskFitsStack():
				cost = self.getUnloadCost()
				children.append( (self.unload(), cost + self.cost))
		elif self.loadIsFeasible():
			if self.stackHasCasks():
				cask_on_CTS = self.getCaskOnThisStack()
				cost = self.getLoadCost(cask_on_CTS)
				children.append( (self.load(), cost + self.cost))

		for neighbour in self.hcb.nodes[self.CTS_pos].neighbours:
			if self.moveIsFeasible(neighbour):
				cost = self.getMoveCost(neighbour)

				def move_to_neighbour(neighbour=neighbour): # trick to define a 'move' method for each feasible neighbour, without the need of
					return self.move(neighbour)         # the search algorithm to pass it any arguments

				children.append( (move_to_neighbour(), cost + self.cost))
		return children


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
