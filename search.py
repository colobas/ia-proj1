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
			-> fcost
			-> gcost
	"""
	def __init__(self, parent, operations, fcost, gcost):
		self.parent = parent
		self.operations = operations
		self.fcost = fcost
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
		print_queue = []
		while node != root:
			line = node.parent.operations[node.prev_operation]['description']
			print_queue.append(line)
			node = node.parent

		print_queue.reverse()

		return (print_queue, self.fcost)

def insert(seq, keys, item, keyfunc):
	"""
	Auxiliary function to efficiently insert objects in order in a sorted list
	"""
	k = keyfunc(item)  # get key
	i = bisect_left(keys, k)  # determine where to insert item
	keys.insert(i, k)  # insert key of item in keys list
	seq.insert(i, item)  # insert the item itself in the corresponding spot	

def uniformCost(root_state):
	"""
	This function implements the Uniform Cost algorithm. It is an uninformed search algorithm, so it only takes each node's fcost into account.
	A queue of possible operations is kept, ordered by cost. The operation taken from the queue is always the one with the smallest fcost available.
	That operation is then performed, which gives us a new node. The new node is checked to see if it is a solution and in that case the algorithm is halted
	and the solution is returned. In the case that the new node isn't a solution, its operations are explored and put inserted into the queue.

	Note: An operation is only put into the queue if the resulting state is not equivalent to an already explored state, because if a state was already explored
	it means we already followed a cheaper path to get to that state

	returns (print_queue, total_cost) where print_queue is a list of strings, each containing the operations involved in the solution
	"""
	explored = [] # list of hashes of explored states
	queue_keys = [] # auxiliary structure to keep the queue in order, by cost
	queue = [] # queue of available moves to take, where the first to come out is the one with the smaller cost

	#initialize queue with root operations

	cur_node = root_state
	for operation in cur_node.operations:
		node = cur_node.operations[operation]['function']() # instantiate the node obtained by performing the operation and add it to the dict, to avoid
		cur_node.operations[operation]['node'] = node       # multiple instatiations
		insert(queue, queue_keys, cur_node.operations[operation], keyfunc = lambda x: x['fcost'])

	while len(queue) != 0:

		todo = queue.pop(0) # get cheapest operation from the queue
		queue_keys.pop(0)
		cur_node = todo['node'] # retrieve the node obtained by performing the operation

		if cur_node.__hash__() in explored: # don't go further if we already explored an equivalent state
			continue

		if cur_node.checksol(): # check if the state is a solution to the problem
			return cur_node.backtrack_sol(root_state)
		else:
			for operation in cur_node.operations:
				node = cur_node.operations[operation]['function']()
				if not node.__hash__() in explored:
					cur_node.operations[operation]['node'] = node
					insert(queue, queue_keys, cur_node.operations[operation], keyfunc = lambda x: x['fcost'])

		explored.append(cur_node.__hash__())

	return None, None
