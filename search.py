from BinHeap import TupleBinHeap

class StateRepresentation:
        """
        This class is an "interface" for the representation of States on the search tree. It's independent of the problem. When defining the problem
        there should be a subclass of this, with implementations of the problem-specific behaviour, in particular the expand method.
        """
        def __init__(self, parent, operations):
                self.parent = parent
                self.operations = operations

        def backtrack_sol(self, root):
                """
                This method traverses the tree backwards, in order to retrieve the solution path. It isn't problem-specific, so it doesn't need to be overridden
                """
                node = self
                print_queue = []
                while node != root:
                        print_queue.append(node.getMoveDescription())
                        node = node.parent

                print_queue.reverse()

                return (print_queue, self.cost)

        def expand(self):
                """
                This method is supposed to be implemented on the problem specific subclass implementation of this class. It is expected to return
                the nodes to which the solver can go from this node.
                """
                pass
def uniformCost(root_state):
        """
        This function implements the Uniform Cost algorithm. It is an uninformed search algorithm, so it only takes each node's cost into account.
        A fringe of possible operations is kept, ordered by cost. This fringe is implemented as a Binary Heap, enhancing performance and making it
        easy to keep track of the next node to be expanded. The node taken from the fringe is always the one with the smallest cost available.
        The new node is checked to see if it is a solution and in that case the algorithm is halted and the solution is returned. 
        In the case that the new node isn't a solution, its operations are explored and put inserted into the fringe.

        returns (print_queue, total_cost) where print_queue is a list of strings, each containing the operations involved in the solution
        """
        fringe = TupleBinHeap() # fringe of available nodes to expand, where the first to come out is the one with the smaller cost
        explored = set() 
        fringe.insert((root_state,0))
        while fringe.currentSize != 0:

                cur_node = fringe.pop()[0]  # get cheapest node to visit from the fringe

                if cur_node.checksol(): # check if the state is a solution to the problem
                        print("node count={}".format(len(explored)))
                        return cur_node.backtrack_sol(root_state)

                explored.add(cur_node.__key__())
                for (child, child_cost) in cur_node.expand():
                        if child.__key__() not in explored:
                                fringe.insert((child,child_cost))


        return None, None

def AStar(root_state):
        """
        This function implements the AStar algorithm. It is an informed search algorithm, so it takes each node's cost and the result of an heuristic 
        into account. A fringe of possible operations is kept, ordered by each node's value of (cost+heuristic). 
        The node taken from the fringe is always the one with the smallest value available for (cost+heuristic).
        The new node is checked to see if it is a solution and in that case the algorithm is halted and the solution is returned. 
        In the case that the new node isn't a solution, its operations are explored and put inserted into the fringe.

        returns (print_queue, total_cost) where print_queue is a list of strings, each containing the operations involved in the solution

        """
        fringe = TupleBinHeap() # fringe of available nodes to expand, where the first to come out is the one with the smaller cost
        explored = set() 
        fringe.insert((root_state,0))
        while fringe.currentSize != 0:

                cur_node = fringe.pop()[0]  # get cheapest node to visit from the fringe

                if cur_node.checksol(): # check if the state is a solution to the problem
                        print("node count={}".format(len(explored)))
                        return cur_node.backtrack_sol(root_state)


                explored.add(cur_node.__key__())
                for (child, child_cost) in cur_node.expand():
                        if child.__key__() not in explored:
                                fringe.insert((child,child_cost+child.heuristic()))


        return None, None
