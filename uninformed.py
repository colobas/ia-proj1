from search import *
from HCB import *
import sys

hcb = HCB(sys.argv[1], sys.argv[2], False)
(lines, cost) = uniformCost(hcb.initial_state)

for line in lines:
	print(line)

print("{}".format(cost))

