#!/usr/bin/python
from heapq import heappop
import numpy as np
from time import sleep

from astar import State, Problem, astar
from csp import *

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
        self.cnet = cnet
        # self.solver = CSPSolver(constraints)

    def triggerStart(self):
        self.network.clear()

        start_state = self.cnet.getRootState()
        # self.solver.AC_3(start_state, node_index)
        Q = [(start_state.cost_to_goal, start_state)]
        D = dict()
        D[start_state.index] = start_state

        return astar, self, self.network, Q, D

    def genNeighbour(self, state):
        """ A neighbour is a state S from the current state,
            where the domain of a variable has been reduced from a domain
            of size > 1 to the singleton set

        """
        new_vertex = state.genRandomVertex() # just the index
        set_trace()
        for value in new_vertex.domain:
            new_state = state.copy()
            new_state[new_vertex].makeAssumption(value)
            AC_3(cnet, new_state, new_vertex)

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

# EOF
