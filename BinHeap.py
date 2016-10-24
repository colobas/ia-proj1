class TupleBinHeap:
	def __init__(self):
		self.heapList = [(None,0)]
		self.currentSize = 0
	def percUp(self,i):
		while i // 2 > 0:
			if self.heapList[i][1] < self.heapList[i // 2][1]:
				tmp = self.heapList[i // 2]
				self.heapList[i // 2] = self.heapList[i]
				self.heapList[i] = tmp
			i = i // 2
	def insert(self,k):
		self.heapList.append(k)
		self.currentSize = self.currentSize + 1
		self.percUp(self.currentSize)

	def percDown(self,i):
		while (i * 2) <= self.currentSize:
			mc = self.minChild(i)
			if self.heapList[i][1] > self.heapList[mc][1]:
				tmp = self.heapList[i]
				self.heapList[i] = self.heapList[mc]
				self.heapList[mc] = tmp
			i = mc

	def minChild(self,i):
		if i * 2 + 1 > self.currentSize:
			return i * 2
		else:
			if self.heapList[i*2][1] < self.heapList[i*2+1][1]:
				return i * 2
			else:
				return i * 2 + 1
	def pop(self):
		retval = self.heapList[1]
		self.heapList[1] = self.heapList[self.currentSize]
		self.currentSize = self.currentSize - 1
		self.heapList.pop()
		self.percDown(1)
		return retval

