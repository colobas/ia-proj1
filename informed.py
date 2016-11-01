from search import *
from HCB import *
import sys

hcb = HCB(sys.argv[1], sys.argv[2], True)
(lines, cost) = AStar(hcb.initial_state)
print("d={}".format(len(lines)))
for line in lines:
	print(line)

print("{}".format(cost))
