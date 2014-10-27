#!/usr/bin/python

from ipdb import set_trace
from astar import State, Problem, astar
from csp import *

class Ngram(Problem):
    def __init__(self, network, cnet, p_rows, p_cols, colors):
        super(Ngram, self).__init__(network)
        self.cnet = cnet
        self.nodes_count = 0
        self.p_rows = p_rows
        self.p_cols = p_cols
        self.colors = colors
        self.mode = "Ngrams"

    """ Send out the initial Q and implementations details
    """
    def triggerStart(self):
        self.network.clear()
        start_state = self.cnet.getRootState()
        start_state.new_paint = start_state[0]

        Q = [(start_state.cost_to_goal, start_state)]
        D = dict()
        D[start_state.index] = start_state

        return astar, self, self.network, Q, D

    """ Generate neighbours from the current state
    """
    def genNeighbour(self, state):
        new_vertex = state.getUnassigned_Nonrandom() 
        for index,value in enumerate(state[new_vertex].domain):
            new_state = state.copy()
            new_state[new_vertex].makeAssumption(index)
            if AC_3_NGRAM(self.cnet, new_state, new_vertex):
                yield new_state

    """ The function to be invoked at the end of a search
    """
    def destructor(self, final_state=None):
        print "Nodes generated --->",self.nodes_count
        self.network.update()
        print'FINISHED'

    """ Paint nodes after iteration in local search
        @param new is the lates state entered
        @param cur is the state before param new
    """
    def updateStates(self, new, cur):
        for vi in new.domains:
            if len(vi.domain) == 1:
                self.network.paint_node(vi.index, self.colors["green"])
            else:
                self.network.paint_node(vi.index, color_pool["black"])
        self.network.update()
# EOF
