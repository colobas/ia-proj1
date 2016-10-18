from bisect import bisect_left

class StateRepresentation:
	def __init__(self, parent, operations, fcost, gcost):
		self.parent = parent
		self.operations = operations
		self.fcost = fcost
		self.gcost = gcost
	def checksol(self):
		pass
	def backtrack_sol(self, root):

		node = self
		print_queue = []
		while node != root:
			line = node.parent.operations[node.prev_operation]['description']
			print_queue.append(line)
			node = node.parent

		print_queue.reverse()

		return (print_queue, self.fcost)

def insert(seq, keys, item, keyfunc):
	k = keyfunc(item)  # get key
	i = bisect_left(keys, k)  # determine where to insert item
	keys.insert(i, k)  # insert key of item in keys list
	seq.insert(i, item)  # insert the item itself in the corresponding spot	

def uniformCost(root_state):
	explored = []
	queue_keys = []
	queue = [] #queue of available moves to take, where the first to come out is the one with the smaller cost
	
	for operation in root_state.operations:
		insert(queue, queue_keys, root_state.operations[operation], keyfunc = lambda x: x['fcost'])
	cur_node = root_state

	while len(queue) != 0:

		todo = queue.pop(0)
		queue_keys.pop(0)
		cur_node = todo['function']()
#		print(cur_node)
#		for op in cur_node.operations:
#			print("\t"+cur_node.operations[op]['description'])

		if cur_node.__hash__() in explored:
			continue
		if cur_node.checksol() != -1:
			return cur_node.backtrack_sol(root_state)
		else:
			for operation in cur_node.operations:
				node = cur_node.operations[operation]['function']()
				if not node.__hash__() in explored:
					insert(queue, queue_keys, cur_node.operations[operation], keyfunc = lambda x: x['fcost'])

		explored.append(cur_node.__hash__())
	return
