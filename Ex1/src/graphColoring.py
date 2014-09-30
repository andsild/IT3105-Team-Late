#!/usr/bin/python
from heapq import heappop
import numpy as np
from time import sleep

from astar import State, Problem, astar
from csp import CSPSolver, CSPState

K = 4 # trivial initial example, later it should be integer 2..10

# If the color scheme is wrong, there will be runtimeerrors.. just saying
color_pool = {  "black"     : [0, 0, 0, 1],
            "white"     : [1, 1, 1, 1],
            "red"       : [1, 0, 0, 1],
            "green"     : [.0, 1, .0, 1],
            "blue"      : [0, 0, 1, 1],
            "yellow"    : [1, .75, 0, 1],
            "lightblue" : [0, 1, .75, 1],
        }

COLORS = [ x for x in color_pool.values() \
          if x is not color_pool["black"] and x is not color_pool["white"]][:K]


class Coloring(Problem):
    def __init__(self, network, cnet):
        super(Coloring, self).__init__(network)
        self.colors = range(len(cnet.domains[0]))
        self.cnet = cnet
        # self.solver = CSPSolver(constraints)

    def triggerStart(self):
        self.network.clear()
        node_index = np.random.randint(low=0, high=self.network.g.num_vertices())
        color_index = np.random.randint(low=0, high=len(self.colors))
        # XXX:
        # node_index = 1
        # color_index = 0
        print "Starting with vertex %d  as color %s" % (node_index, "blue")

        start_node = self.network.g.vertex(node_index)
        start_color = self.colors[color_index]

        init_domains = [ deepcopy(li) for li in cnet.domains]
        init_domains[node_index] = [color_index]

        start_state = CSPState(None, init_domains, (start_node, start_color))

        # self.solver.AC_3(start_state, node_index)

        #TODO: this Q is similar in all "problem" classes
        Q = [(start_state.cost_to_goal, start_state)]
        D = dict()
        D[start_state.index] = start_state

        # self.network.update()
        self.network.paint_node(start_node, start_color)

        return astar, self, self.network, Q, D

    def genNeighbour(self, state):
        """ A neighbour is a state S from the current state,
            where the domain of a variable has been reduced from a domain
            of size > 1 to the singleton set

        """
        new_vertex = state.genRandomVertex()
        print "picking %s as new for neigh" % (str(new_vertex))
        if new_vertex is not None:
            return self.solver.AC_3(state, new_vertex)
        return []

    def destructor(self, Q):
        if Q:
            _, state = heappop(Q)
            for index,dom in enumerate(state.domains):
                if len(dom) == 1:
                    self.network.paint_node(index, COLORS[dom[0]])
        print "FINISHED"

    def updateStates(self, new, cur):
        if new.pred == cur:
            self.network.paint_node(*new.getLatestAddition())
        else:
            # TODO: re-check EVERYTHING
            for index,dom in enumerate(new.domains):
                if len(dom) == 1:
                    self.network.paint_node(index, COLORS[dom[0]])
                else:
                    self.network.paint_node(index, color_pool["black"])

            # self.network.paint_node(*new.getLatestAddition())
        # self.network.update()

