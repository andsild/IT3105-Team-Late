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
            "brown"     : [0.66, 0.38, 0.18, 1],
            "purple"    : [0.66, 0, 1, 1],
            "orange"    : [1, 0.56, 0, 1],
            "pink"      : [1, 0, 0.8, 1],
            "grey"      : [0.5, 0.5, 0.5, 1],
        }

class Coloring(Problem):
    def __init__(self, network, cnet, COLORS):
        super(Coloring, self).__init__(network)
        self.cnet = cnet
        self.colors = [x for x in COLORS]
        self.mode = "VC"
       # self.solver = CSPSolver(constraints)

    def triggerStart(self):
        self.network.clear()

        start_state = self.cnet.getRootState()
        start_state.new_paint = start_state[start_state.getUnassigned()]
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
        new_vertex = state.getUnassigned_Nonrandom() # just the index
        # new_vertex = self.network[state.new_paint.index]

        for value in state[new_vertex].domain:
            new_state = state.copy()
            # set_trace()
            new_state[new_vertex].makeAssumption(value)
            if AC_3(self.cnet, new_state, new_vertex):
                yield new_state

    def destructor(self, final_state):
        set_trace()
        if final_state:
            for vi in final_state.domains:
                if len(vi.domain) == 1:
                    self.network.paint_node(vi.index, self.colors[vi.domain[0]])
        print "FINISHED"

    def updateStates(self, new, cur):
        for vi in new.domains:
            if len(vi.domain) == 1:
                self.network.paint_node(vi.index, self.colors[vi.domain[0]])
            else:
                self.network.paint_node(vi.index, color_pool["black"])
        self.network.update()

# EOF
