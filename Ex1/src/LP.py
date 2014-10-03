#!/usr/bin/python
from heapq import heappop
import numpy as np
from time import sleep

from astar import State, Problem, astar
from csp import *

class LPSolver(Problem):
    def __init__(self, network, cnet):
        super(Problem, self).__init__(network)
        self.cnet = cnet
        self.mode = "LP"
        # self.solver = CSPSolver(constraints)

    def triggerStart(self):
        self.network.clear()
        pass

        start_state = self.cnet.getRootState()
        start_state.newPaint = start_state[start_state.getUnassigned()]
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
        pass

    def destructor(self, final_state):
        pass

    def updateStates(self, new, cur):
        pass

# EOF

