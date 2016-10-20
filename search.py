from bisect import bisect_left

class StateRepresentation:
	"""
	This class is an "interface" for the representation of States on the search tree. It's independent of the problem. When defining the problem
	there should be a subclass of this, with implementations of the problem-specific behaviour.

	Remarks:
		-> self.parent is the node that preceded this one
		-> self.operations is a dict of the operations available to be performed on this node. The values of this dict are also dicts,
		and they contain the following fields:
			-> function : function pointer to the function that performs the operation
			-> description : description of the operation, to be used when printing the final solution
			-> cost
			-> gcost
	"""
	def __init__(self, parent, operations, cost, gcost):
		self.parent = parent
		self.operations = operations
		self.cost = cost
		self.gcost = gcost
	def checksol(self):
		"""
		This method should be implemented on the problem-specific subclass of this class. It's job is to check whether the current node is a solution to the problem
		"""
		pass

	def backtrack_sol(self, root):
		"""
		This method traverses the tree backwards, in order to retrieve the solution path. It isn't problem-specific, so it doesn't need to be overridden
		"""
		node = self
		print_fringe = []
		while node != root:
			line = node.parent.operations[node.prev_operation]['description']
			print_fringe.append(line)
			node = node.parent

		print_fringe.reverse()

		return (print_fringe, self.cost)


def uniformCost(root_state):
	"""
	This function implements the Uniform Cost algorithm. It is an uninformed search algorithm, so it only takes each node's cost into account.
	A fringe of possible operations is kept, ordered by cost. The operation taken from the fringe is always the one with the smallest cost available.
	That operation is then performed, which gives us a new node. The new node is checked to see if it is a solution and in that case the algorithm is halted
	and the solution is returned. In the case that the new node isn't a solution, its operations are closed and put inserted into the fringe.

	returns (print_fringe, total_cost) where print_fringe is a list of strings, each containing the operations involved in the solution
	"""
	closed = [] # list of hashes of closed states
	fringe = dict() # fringe of available moves to take, where the first to come out is the one with the smaller cost

	#initialize fringe with root operations

	cur_node = root_state
	for operation in cur_node.operations:
		node = cur_node.operations[operation]['function']() # instantiate the node obtained by performing the operation and add it to the dict, to avoid
		cur_node.operations[operation]['node'] = node       #                                                                     multiple instatiations
		fringe[node.__hash__()] = cur_node.operations[operation]

	while len(fringe) != 0:

		todo = min(fringe.values(), key=lambda x: x['cost']) # get cheapest operation from the fringe
		#print('------------fringe values:------------------')
		#for el in fringe.values():
		#	print('\t'+el['description'] + '|| {}'.format(el['cost']))
		#print('\t MIN VALUE')
		#print(todo['description'] + '|| {}'.format(todo['cost']))

		cur_node = todo['node'] # retrieve the node obtained by performing the operation
		fringe.pop(cur_node.__hash__())

		if cur_node.__hash__() in closed: # don't go further if we already closed an equivalent state
			continue

		closed.append(cur_node.__hash__())

		if cur_node.checksol(): # check if the state is a solution to the problem
			return cur_node.backtrack_sol(root_state)
		else:
			for operation in cur_node.operations:
				node = cur_node.operations[operation]['function']()
				if not node.__hash__() in closed:
					dont = False
					if node.__hash__() in fringe:
						op = fringe[node.__hash__()]	# if there's an equivalent state in the fringe, we only add this if it
						if op['cost'] > node.cost:      #                                                   has a smaller cost
							fringe.pop(op['node'].__hash__())
						else:
							dont = True
						break
					if not dont:
						cur_node.operations[operation]['node'] = node
						fringe[node.__hash__()] = cur_node.operations[operation]


	return None, None

def AStar(root_state):
	"""
	This function implements the Uniform Cost algorithm. It is an uninformed search algorithm, so it only takes each node's cost into account.
	A fringe of possible operations is kept, ordered by cost. The operation taken from the fringe is always the one with the smallest cost available.
	That operation is then performed, which gives us a new node. The new node is checked to see if it is a solution and in that case the algorithm is halted
	and the solution is returned. In the case that the new node isn't a solution, its operations are closed and put inserted into the fringe.

	returns (print_fringe, total_cost) where print_fringe is a list of strings, each containing the operations involved in the solution
	"""
	closed = [] # list of hashes of closed states
	fringe = dict() # fringe of available moves to take, where the first to come out is the one with the smaller cost

	#initialize fringe with root operations

	cur_node = root_state
	for operation in cur_node.operations:
		node = cur_node.operations[operation]['function']() # instantiate the node obtained by performing the operation and add it to the dict, to avoid
		cur_node.operations[operation]['node'] = node       # multiple instatiations
		fringe[node.__hash__()] = cur_node.operations[operation]

	while len(fringe) != 0:

		todo = min(fringe.values(), key=lambda x: x['cost'] + x['node'].heuristic()) # get cheapest operation from the fringe
		cur_node = todo['node'] # retrieve the node obtained by performing the operation
		fringe.pop(cur_node.__hash__())

		if cur_node.__hash__() in closed: # don't go further if we already closed an equivalent state
			continue

		if cur_node.checksol(): # check if the state is a solution to the problem
			return cur_node.backtrack_sol(root_state)
		else:
			for operation in cur_node.operations:
				node = cur_node.operations[operation]['function']()
				if not node.__hash__() in closed:
					dont = False
					if node.__hash__() in fringe:
						op = fringe[node.__hash__()]	# if there's an equivalent state in the fringe, we only add this if it
						if op['cost'] > node.cost:      # has a smaller cost
							fringe.pop(op['node'].__hash__())
						else:
							dont = True
						break
					if not dont:
						cur_node.operations[operation]['node'] = node
						fringe[node.__hash__()] = cur_node.operations[operation]

		closed.append(cur_node.__hash__())

	return None, None
