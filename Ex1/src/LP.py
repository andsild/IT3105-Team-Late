#!/usr/bin/python
from heapq import heappop
import numpy as np
from time import sleep

from astar import State, Problem, astar
from network import colors
from csp import *

from pulp import *

class LPSolver(Problem):
    def __init__(self, network, cnet):
        super(LPSolver, self).__init__(network)
        self.cnet = cnet
        self.mode = "LP"
        # self.solver = CSPSolver(constraints)

    def simplexsolve(self, state):
        prob = LpProblem("node_relax", LpMinimize)
        arg_list = state.domains

        return 1

    def fathomtest(self, solution):
        pass
        # def test1():
        #     return solution.bound..
        # def test2():
        #     not solvable
        # def test3():
        #     if integer:
        #
        # if all([ op(solution) for op in [test1, test2, test3])
        #     return True
        # return False

    def triggerStart(self):
        self.network.clear()

        start_state = self.cnet.getRootState()
        start_state.newPaint = start_state[start_state.getUnassigned()]
        # self.solver.AC_3(start_state, node_index)
        Q = [(start_state.cost_to_goal, start_state)]
        D = dict()
        D[start_state.index] = start_state
        self.zstar = float("-inf")

        return astar, self, self.network, Q, D


    def genNeighbour(self, state):
        """ A neighbour is a state S from the current state,
            where the domain of a variable has been reduced from a domain
          of size > 1 to the singleton set

        """
        new_vertex = state.getUnassigned_Nonrandom() # just the index
        # new_vertex = self.network[state.newPaint.index]

        for index,value in enumerate(state[new_vertex].domain):
            new_state = state.copy()
            self.network.insertVertex( (new_state.depth, index))
            new_state[new_vertex].makeAssumption(value)
            sol = self.simplexsolve(new_state)
            if self.fathomtest(sol):
                new_state.cost_to_goal = sol . something
                yield new_state

        self.network.update()

    def destructor(self, final_state):
        # if final_state:
        #     for vi in final_state.domains:
        #         if len(vi.domain) == 1:
        #             self.network.paint_node(vi.index, colors["seen"])
        print "FINISHED"
        self.network.update()

    def updateStates(self, new, cur):
        pass
        # for vi in new.domains:
        #     if len(vi.domain) == 1:
        #         self.network.paint_node(vi.index, colors["seen"])
        #     else:
        #         self.network.paint_node(vi.index, colors["unused"])
        # self.network.update()

# EOF

