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
			print_queue.append(node.parent.operations[node.prev_operation])

		print_queue = print_queue.reverse()
		for line in print_queue:
			print(line)

		return print_queue

def insert(seq, keys, item, keyfunc):
	k = keyfunc(item)  # get key
	i = bisect_left(keys, k)  # determine where to insert item
	keys.insert(i, k)  # insert key of item in keys list
	seq.insert(i, item)  # insert the item itself in the corresponding spot	

def uniformCost(root_state):
	queue_keys = []
	queue = [] #queue of available moves to take, where the first to come out is the one with the smaller cost
	
	for operation in root_state.operations:
		insert(queue, queue_keys, root_state.operations[operation], keyfunc = lambda x: x['fcost'])
	cur_node = root_state

	while len(queue) != 0:
		todo = queue.pop(0)
		print(todo['description'])
		cur_node = todo['function']()

		if cur_node.checksol() != -1:
			return cur_node.backtrack_sol()
		else:
			for operation in cur_node.operations:
				insert(queue, queue_keys, cur_node.operations[operation], keyfunc = lambda x: x['fcost'])

